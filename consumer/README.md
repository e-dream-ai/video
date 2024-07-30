# python backend client

### variables

`BACKEND_URL` and `API_KEY` are configuration variables that determine the target environment for your API requests, are located on `client/api_client.py` file

target backend url

```python
BACKEND_URL = "http://localhost:8081/api/v1"
```

apikey to authorize backend requests

```python
API_KEY = "http://localhost:8081/api/v1"
```

### setup client

Import ApiClient and create an instance to connect with backend

```python
from client.api_client import ApiClient

client = ApiClient()
```

### run

run `run.py` file to test api client with this command

```bash
python consumer/run.py
```
