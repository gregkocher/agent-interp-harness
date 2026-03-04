"""Lightweight reverse proxy for capturing API requests.

Sits between the Claude Agent SDK and the real API to capture:
- System prompt (Claude Code's built-in + user's appended)
- Tool definitions (JSON schemas for Read, Write, Bash, etc.)
- Compaction events (when message count drops, captures summarized messages)
- Sampling parameters (model, temperature, max_tokens)
"""

from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from aiohttp import ClientSession, web

logger = logging.getLogger(__name__)


def _hash(obj: object) -> str:
    """Stable SHA-256 hash of a JSON-serializable object."""
    raw = json.dumps(obj, sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(raw.encode()).hexdigest()[:16]}"


class CaptureProxy:
    """Reverse proxy that logs API request metadata to JSONL."""

    def __init__(self) -> None:
        self._target_url: str = ""
        self._log_path: Path | None = None
        self._site: web.TCPSite | None = None
        self._runner: web.AppRunner | None = None
        self._request_index = 0
        self._prev_message_count = 0
        self._prev_system_hash: str | None = None
        self._prev_tools_hash: str | None = None

    async def start(self, target_url: str, log_path: Path) -> int:
        """Start the proxy server. Returns the assigned port."""
        self._target_url = target_url.rstrip("/")
        self._log_path = log_path
        self._request_index = 0
        self._prev_message_count = 0
        self._prev_system_hash = None
        self._prev_tools_hash = None

        app = web.Application()
        app.router.add_route("*", "/{path:.*}", self._handle)

        self._runner = web.AppRunner(app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, "127.0.0.1", 0)
        await self._site.start()

        # Get the actual assigned port
        assert self._site._server is not None
        port = self._site._server.sockets[0].getsockname()[1]
        logger.info("Capture proxy started on port %d -> %s", port, self._target_url)
        return port

    async def stop(self) -> None:
        """Stop the proxy server."""
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
            self._site = None
            logger.info("Capture proxy stopped")

    async def _handle(self, request: web.Request) -> web.StreamResponse:
        """Forward request to target, log Messages API calls."""
        target = f"{self._target_url}/{request.match_info['path']}"
        body = await request.read()

        # Log Messages API requests
        is_messages = request.method == "POST" and "/messages" in request.path
        if is_messages and body:
            try:
                self._log_request(json.loads(body))
            except Exception:
                logger.exception("Failed to log API request")

        # Forward headers (drop host, it'll be set by aiohttp)
        headers = {
            k: v for k, v in request.headers.items()
            if k.lower() not in ("host", "content-length", "transfer-encoding")
        }

        async with ClientSession() as session:
            async with session.request(
                request.method, target, headers=headers, data=body
            ) as resp:
                # Build response, preserving status and safe headers
                response = web.StreamResponse(status=resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in (
                        "content-length", "transfer-encoding", "content-encoding",
                    ):
                        response.headers[k] = v
                await response.prepare(request)

                # Stream response body
                async for chunk in resp.content.iter_any():
                    await response.write(chunk)

                await response.write_eof()
                return response

    def _log_request(self, data: dict) -> None:
        """Extract and log metadata from a Messages API request."""
        if not self._log_path:
            return

        self._request_index += 1

        system = data.get("system")
        tools = data.get("tools")
        messages = data.get("messages", [])
        message_count = len(messages)

        system_hash = _hash(system) if system else None
        tools_hash = _hash(tools) if tools else None

        # Detect compaction: message count dropped
        is_compaction = (
            message_count < self._prev_message_count
            and self._prev_message_count > 0
        )

        # Build log entry
        entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_index": self._request_index,
            "model": data.get("model"),
            "sampling_params": {
                k: data.get(k)
                for k in ("temperature", "max_tokens", "top_p", "top_k")
                if data.get(k) is not None
            },
            "message_count": message_count,
        }

        # System prompt: full on first or change, hash-only otherwise
        if system_hash != self._prev_system_hash:
            entry["system_prompt"] = system
            entry["system_prompt_hash"] = system_hash
            self._prev_system_hash = system_hash
        else:
            entry["system_prompt_hash"] = system_hash

        # Tools: full on first or change, hash-only otherwise
        if tools_hash != self._prev_tools_hash:
            entry["tools"] = tools
            entry["tools_hash"] = tools_hash
            self._prev_tools_hash = tools_hash
        else:
            entry["tools_hash"] = tools_hash

        # Compaction: capture the summarized messages
        entry["is_compaction"] = is_compaction
        if is_compaction:
            entry["compacted_messages"] = messages
            logger.info(
                "Compaction detected: message count %d -> %d",
                self._prev_message_count, message_count,
            )

        self._prev_message_count = message_count

        # Append to JSONL
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._log_path, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")


def get_target_url(provider: str, base_url: str | None) -> str:
    """Resolve the real API URL for a given provider."""
    if base_url:
        return base_url
    if provider == "openrouter":
        return "https://openrouter.ai/api"
    # Default to Anthropic API for all other providers.
    # For bedrock/vertex, Claude Code may or may not route through
    # ANTHROPIC_BASE_URL — if it doesn't, the proxy will simply
    # receive no requests and api_captures.jsonl will be empty.
    return "https://api.anthropic.com"
