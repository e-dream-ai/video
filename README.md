# video service

## About

Video and image ingestion service running on RunPod Serverless with GPU acceleration.

- Transcodes video to H.265/HEVC 1080p using NVIDIA NVENC (with CPU fallback)
- Generates thumbnails and filmstrip frames
- Converts images to WebP format
- Calculates MD5 hashes
- Uses ffmpeg with CUDA hardware acceleration for decoding and encoding

## Job Types

| Type        | Input                     | Description                   |
| ----------- | ------------------------- | ----------------------------- |
| `video`     | `dream_uuid`, `extension` | Full video ingestion pipeline |
| `image`     | `dream_uuid`, `extension` | Image conversion to WebP      |
| `md5`       | `dream_uuid`              | MD5 hash of processed video   |
| `filmstrip` | `dream_uuid`              | Generate filmstrip frames     |

## Requirements

- Python 3.12.x
- ffmpeg
- ImageMagick (for image WebP conversion)
- NVIDIA GPU with NVENC support (optional, falls back to CPU)

## Run Locally

### Install dependencies

```bash
brew install ffmpeg imagemagick
```

### Install pyenv-virtualenv (recommended)

```bash
pyenv virtualenv 3.12.2 edream_video
pyenv activate edream_video
```

### Install requirements

```bash
pip install -r requirements.txt
```

### Install edream SDK

```bash
git submodule init
git submodule update --remote
pip install -e python-api
```

### Set environment variables

```bash
cp .env.example .env
# Edit .env with your BACKEND_URL and BACKEND_API_KEY
```

### Run handler locally

```bash
python handler.py --test_input test_input.json
```

Edit `test_input.json` with a real `dream_uuid` to test.

## Docker

### Build

```bash
docker build --platform linux/amd64 -t dream-ingestion .
```

### Run (CPU, no GPU)

```bash
docker run --platform linux/amd64 \
  -e BACKEND_URL=<backend-url> \
  -e BACKEND_API_KEY=<backend-apikey> \
  dream-ingestion \
  python3 -u /app/handler.py --test_input /app/test_input.json
```

### Run (GPU, on NVIDIA machine)

```bash
docker run --gpus all \
  -e BACKEND_URL=<backend-url> \
  -e BACKEND_API_KEY=<backend-apikey> \
  dream-ingestion
```
