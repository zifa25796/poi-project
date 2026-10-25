"""
VoiceLine HTTP API Server
手机通过局域网触发播放。

由 app.py 作为 daemon 线程启动；也可独立运行：
    python api_server.py
"""

import os
import tempfile
import logging
import time
import uuid
import ipaddress
from datetime import datetime

from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask

from hourly_chime import safe_speak, chime, _get_vl
from voice_line.logging_setup import configure_logging

configure_logging()
logger = logging.getLogger("daily.api")

app = FastAPI(title="VoiceLine API", version="0.2.0")


def request_origin(request: Request) -> str:
    if request.headers.get("cf-ray") or request.headers.get("cf-connecting-ip"):
        return "WEB"
    if request.headers.get("x-forwarded-for") or request.headers.get("forwarded"):
        return "WEB"
    try:
        return "LOCAL" if ipaddress.ip_address(request.client.host).is_loopback else "WEB"
    except (ValueError, AttributeError):
        return "WEB"


@app.middleware("http")
async def log_request(request: Request, call_next):
    request_id = uuid.uuid4().hex[:8]
    origin = request_origin(request)
    started = time.monotonic()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Request failed | id=%s %s %s", request_id, request.method, request.url.path, extra={"category": origin})
        raise
    response.headers["X-Request-ID"] = request_id
    if request.url.path != "/favicon.ico" or response.status_code >= 500:
        level = logging.ERROR if response.status_code >= 500 else logging.WARNING if response.status_code >= 400 else logging.INFO
        logger.log(level, "Request | id=%s %s %s status=%s elapsed=%.3fs client=%s",
                   request_id, request.method, request.url.path, response.status_code,
                   time.monotonic() - started, request.client.host if request.client else "unknown",
                   extra={"category": origin})
    return response


@app.get("/")
def root():
    """健康检查"""
    return {"status": "online", "time": datetime.now().strftime("%H:%M:%S")}


@app.get("/say")
async def say(text: str = Query(..., description="要播放的文本"),
              background_tasks: BackgroundTasks = None):
    """后台线程播放，立即返回"""
    if not text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")
    background_tasks.add_task(safe_speak, text.strip())
    return {"ok": True, "text": text.strip()}


@app.get("/say/local")
def say_local(text: str = Query(..., description="要播放的文本")):
    """返回 WAV 音频文件，手机浏览器直接播放。"""
    if not text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tmp.close()

    _get_vl().speak_to_file(text.strip(), tmp.name)

    return FileResponse(
        tmp.name,
        media_type="audio/wav",
        filename="voice.wav",
        background=BackgroundTask(os.unlink, tmp.name),
    )


@app.get("/time")
def announce_time():
    """播报当前时间 — 复用 hourly_chime.chime()"""
    phrase = chime()
    return {"ok": True, "text": phrase}


@app.get("/stats")
def stats():
    """词库统计"""
    return {"stats": _get_vl().stats()}


@app.get("/missing")
def missing(top: int = Query(20, ge=1, le=1000)):
    return {"missing": _get_vl().missing(top)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000, log_config=None, access_log=False)
