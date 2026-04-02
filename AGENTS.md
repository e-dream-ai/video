# AGENTS.md — video

## Overview

RunPod-based video and image ingestion service with GPU acceleration. Transcodes video to H.265/HEVC, generates thumbnails and filmstrip frames, converts images to WebP, and calculates MD5 hashes.

## Stack

- **Language:** Python 3.12
- **Container Base:** nvidia/cuda:12.8.0-cudnn-devel-ubuntu22.04
- **Framework:** RunPod SDK
- **Tools:** FFmpeg (with CUDA/NVENC), ImageMagick
- **Dependencies:** runpod, requests, python-dotenv, edream_sdk, Pillow, boto3

## Project Structure

```
handler.py          # Main RunPod handler for job processing
clients/            # API client implementations
utils/              # Utility functions
constants/          # Application constants
Dockerfile          # Multi-stage build (ffmpeg builder + runtime)
entrypoint.sh       # Container entrypoint
python-api/         # SDK submodule
```

## Commands

```bash
pip install -r requirements.txt
python handler.py --test_input test_input.json       # Run locally with test input
docker build --platform linux/amd64 -t dream-ingestion .  # Build container
docker run --gpus all -e BACKEND_URL=... dream-ingestion   # Run container
```

## Key Patterns

- RunPod serverless job handler pattern
- Job type routing: video, image, md5, filmstrip
- GPU acceleration via NVIDIA NVENC (with CPU fallback)
- Multi-stage Docker builds for optimized images
- Environment variables: BACKEND_URL, BACKEND_API_KEY

## Deployment

RunPod Serverless with GPU support.
