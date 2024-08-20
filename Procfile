web: gunicorn app:app
worker: bash -c "git submodule update --init --recursive && pip install -e python-api && python worker.py"