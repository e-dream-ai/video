FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ffmpeg \
        imagemagick \
        python3 \
        python3-pip \
        git \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

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
