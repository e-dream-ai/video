# video service

- Python, Flask, runs on Heroku
- Provides extraction of thumbnail and filmstrip images, verifies correctness of resolution, format, bps etc (we can do a trial decode), removes sound, transcodes if needed.
- Uses ffmpeg.
- Queues for input and output
- Eventually we’ll need GPUs when we get as far as upscaling, Stable Diffusion, and aesthetic models. So we may migrate this to AWS, Modal, or Replicate since Heroku doesn’t have them.

#### Adding worker to video service

```sh
heroku ps:scale worker=1 -a video-service
```
