FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04 AS ffmpeg-builder

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        yasm \
        nasm \
        git \
        wget \
        libx264-dev \
        libx265-dev \
        libnuma-dev \
        libvpx-dev \
        libfdk-aac-dev \
        libmp3lame-dev \
        libopus-dev \
        libfreetype6-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN git clone https://git.videolan.org/git/ffmpeg/nv-codec-headers.git /tmp/nv-codec-headers && \
    cd /tmp/nv-codec-headers && \
    make install

RUN git clone --depth 1 --branch n6.1.2 https://git.ffmpeg.org/ffmpeg.git /tmp/ffmpeg && \
    cd /tmp/ffmpeg && \
    ./configure \
        --prefix=/usr/local \
        --enable-gpl \
        --enable-nonfree \
        --enable-cuda-nvcc \
        --enable-libnpp \
        --enable-cuvid \
        --enable-nvenc \
        --enable-nvdec \
        --enable-libx264 \
        --enable-libx265 \
        --enable-libvpx \
        --enable-libfdk-aac \
        --enable-libmp3lame \
        --enable-libopus \
        --enable-libfreetype \
        --extra-cflags="-I/usr/local/cuda/include" \
        --extra-ldflags="-L/usr/local/cuda/lib64" \
    && make -j$(nproc) \
    && make install

FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

COPY --from=ffmpeg-builder /usr/local/bin/ffmpeg /usr/local/bin/ffmpeg
COPY --from=ffmpeg-builder /usr/local/bin/ffprobe /usr/local/bin/ffprobe
COPY --from=ffmpeg-builder /usr/local/lib/*.so* /usr/local/lib/

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        imagemagick \
        python3 \
        python3-pip \
        git \
        libx264-163 \
        libx265-199 \
        libvpx7 \
        libfdk-aac2 \
        libmp3lame0 \
        libopus0 \
        libfreetype6 \
        libnuma1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/* \
    && ldconfig

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY handler.py /app/handler.py
COPY clients/ /app/clients/
COPY utils/ /app/utils/
COPY constants/ /app/constants/

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN mkdir -p /app/assets

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["python3", "-u", "/app/handler.py"]
