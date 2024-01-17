# video service

- Python, Flask, runs on Heroku
- Provides extraction of thumbnail and filmstrip images, verifies correctness of resolution, format, bps etc (we can do a trial decode), removes sound, transcodes if needed.
- Uses ffmpeg.
- Queues for input and output
- Eventually we’ll need GPUs when we get as far as upscaling, Stable Diffusion, and aesthetic models. So we may migrate this to AWS, Modal, or Replicate since Heroku doesn’t have them.

## Run service

### Locally

Start redis service on mac

```bash
 brew services restart redis
```

Run worker

```bash
 python worker.py
```

Run app

```bash
 python worker.py
```

**Note for macOS**

Port 5000 may be in use by another program. Either identify and stop that program, or start the server with a different port.
On macOS, try disabling the 'AirPlay Receiver' service from System Preferences -> General -> AirDrop & Handoff.

### Stage/Production Server

#### Adding worker to video service

```sh
heroku ps:scale worker=1 -a video-service
```
