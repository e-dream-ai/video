# video service

## Requeriments

- python 3.12.x
- redis 7.2.x
- [heroku-22 stack](https://devcenter.heroku.com/articles/heroku-22-stack) (only for deploys, not need to install locally)

## About

### Notes

- Python worker and python Flask server runs on Heroku.
- Provides extraction of thumbnail and filmstrip images, verifies correctness of resolution, format, bps etc (we can do a trial decode), removes sound, transcodes if needed.
- Uses ffmpeg.
- Queues for input and output.
- Eventually we’ll need GPUs when we get as far as upscaling, Stable Diffusion, and aesthetic models. So we may migrate this to AWS, Modal, or Replicate since Heroku doesn’t have them.

## Run service

### Locally

Install [ffmpeg](https://ffmpeg.org/download.html), on macOS

```bash
brew install ffmpeg
```

Install [pyenv](https://github.com/pyenv/pyenv) and config python 3.12.x, on macOS

```bash
brew install pyenv
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
pyenv install 3.12.1
pyenv global 3.12.1
```

Install [redis](https://redis.io/docs/install/install-redis/), on macOS

```bash
brew install redis
```

Start redis service on mac

```bash
brew services start redis
```

Install requirements

```bash
pip install -r requirements.txt
```

Run worker

```bash
 python worker.py
```

Run flask app on other terminal

```bash
 flask run
```

Now flask server is running and waiting for requests to process videos

**Note for macOS**

Port 5000 may be in use by another program. Either identify and stop that program, or start the server with a different port.
On macOS, try disabling the 'AirPlay Receiver' service from System Preferences -> General -> AirDrop & Handoff.

### Stage/Production Server

#### Config

##### Adding heroku ffmpeg buildpacks to video service

```bash
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git -a video-server
```

##### Adding heroku redis add-on to video service

```bash
heroku addons:create rediscloud:30 -a video-server
```

##### Adding worker to video service

```bash
heroku ps:scale worker=1 -a video-service
```

##### Adding Procfile

Add Procfile and make sure both dynos are running

```
web: gunicorn app:app
worker: python worker.py
```

#### Deploy

- When you merge a change from a branch feat/name or fix/name to stage, or push changes directly to stage a deploy is trigger automatically on heroku.
