import os, tempfile, glob, re
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import yt_dlp

API_KEY = os.getenv("API_KEY")  # simple shared secret
MAX_MINUTES = int(os.getenv("MAX_DURATION_MIN", "120"))  # optional safety

app = FastAPI(title="yt2mp3", version="1.0")

class Job(BaseModel):
    url: str

def sanitize_filename(name: str) -> str:
    return re.sub(r'[^-\w\.\(\) ]', '_', name)[:120]

@app.post("/yt2mp3")
def yt2mp3(job: Job, x_api_key: str = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    url = job.url.strip()
    if not url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid URL")

    with tempfile.TemporaryDirectory() as tmp:
        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{tmp}/%(id)s.%(ext)s",
            "noplaylist": True,
            "quiet": True,
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                duration = info.get("duration") or 0
                if MAX_MINUTES and duration > MAX_MINUTES * 60:
                    raise HTTPException(status_code=413, detail=f"Video too long (> {MAX_MINUTES} min).")
                title = sanitize_filename(info.get("title") or info.get("id") or "audio")
        except yt_dlp.utils.DownloadError as e:
            raise HTTPException(status_code=422, detail=f"Download error: {e}")

        # find produced MP3
        files = glob.glob(f"{tmp}/*.mp3")
        if not files:
            raise HTTPException(status_code=500, detail="MP3 not produced.")
        mp3_path = files[0]
        filename = f"{title}.mp3"

        headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
        return FileResponse(mp3_path, media_type="audio/mpeg", filename=filename, headers=headers)

@app.get("/healthz")
def health():
    return JSONResponse({"ok": True})
