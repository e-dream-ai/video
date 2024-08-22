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

#### Install FFMPEG

Install [ffmpeg](https://ffmpeg.org/download.html), on macOS

```bash
brew install ffmpeg
```

#### Install pyenv-virtualenv (recommended)

Install pyenv-virtualenv following [this](https://github.com/pyenv/pyenv-virtualenv?tab=readme-ov-file#installation) documentation and config python 3.12.x

##### create pyenv

```bash
pyenv virtualenv 3.12.2 edream_video
```

##### activate pyenv

```bash
pyenv activate edream_video
```

#### Install redis

Install [redis](https://redis.io/docs/install/install-redis/), on macOS

```bash
brew install redis
```

Start redis service on mac

```bash
brew services start redis
```

#### Install requirements

```bash
pip install -r requirements.txt
```

#### install edream sdk

Fetch submodule with init

```bash
git submodule init
```

Update (every time that is needed)

```bash
git submodule update --remote
```

Install locally

```bash
pip install -e python-api
```

#### Run

On two different terminals, run flask server and worker

Run flask app on other terminal

```bash
 flask run
```

Run worker

```bash
 python worker.py
```

Now flask server is running and waiting for requests to process videos

**Note for macOS**

Port 5000 may be in use by another program. Either identify and stop that program, or start the server with a different port.
On macOS, try disabling the 'AirPlay Receiver' service from System Preferences -> General -> AirDrop & Handoff.

### Stage/Production Server

#### Config

These settings are already in place for stage/production environments, just follow the steps if you need to set up a new environment or if you need to update any settings.

##### FFMPEG

Adding heroku ffmpeg buildpacks to video service

```bash
heroku buildpacks:add --index 1 https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git -a video-service
```

##### Redis

Adding heroku redis add-on to video service

```bash
heroku addons:create rediscloud:30 -a video-service
```

##### python-api sdk

Installing python-api is different from local, heroku needs to set a ssh-private-key to install edream_sdk package from [requirements.txt](requirements.txt), follow next steps to set up automatic installation. This [documentation](https://elements.heroku.com/buildpacks/debitoor/ssh-private-key-buildpack) helps setup ssh-private-key-buildpack.

##### ssh-private-key-buildpack

```bash
heroku buildpacks:set --index 1 https://github.com/debitoor/ssh-private-key-buildpack.git -a video-service
```

Set `SSH_KEY`, replace `cat path/to/your/keys/id_rsa` with edream id_rsa location (github deploy key). Deploy key should be setup on python-api repo.

```bash
heroku config:set SSH_KEY=$(cat path/to/your/keys/id_rsa | base64) -a video-service
```

##### Worker

Adding worker to video service

```bash
heroku ps:scale worker=1 -a video-service
```

##### Procfile

Adding Procfile

Add Procfile and make sure both dynos are running

```
web: gunicorn app:app
worker: python worker.py
```

#### Deploy

- When you merge a change from a branch feat/name or fix/name to stage, or push changes directly to stage a deploy is trigger automatically on heroku.
