# yt2mp3-api

A lightweight API that converts YouTube videos to MP3 audio using FastAPI, yt-dlp, and ffmpeg.  
Built for deployment on [Render](https://render.com) (Docker environment) and integration with automation tools like [n8n](https://n8n.io).

## Features
- 🎵 Download best audio from YouTube and convert to MP3
- 🚀 REST API endpoint (`/yt2mp3`) with JSON input
- 🔒 API key protection via `X-API-Key` header
- ⏱ Optional duration limit (`MAX_DURATION_MIN`)
- 🩺 Health check endpoint (`/healthz`)

## Quickstart

### Request
```bash
curl -X POST "https://YOUR_RENDER_URL/yt2mp3" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"url":"https://www.youtube.com/watch?v=VIDEO_ID"}' \
  --output audio.mp3
