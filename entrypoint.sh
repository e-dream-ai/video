#!/usr/bin/env bash
set -e

echo "Checking NVENC encoder availability..."
if ffmpeg -hide_banner -encoders 2>/dev/null | grep -q hevc_nvenc; then
    echo "NVENC hardware encoder: AVAILABLE"
else
    echo "NVENC hardware encoder: NOT AVAILABLE (will use CPU fallback)"
fi

exec "$@"
