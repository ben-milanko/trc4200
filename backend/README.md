# Visualisation server

## How to run

1. Make a virtualenv

2. Install requirements:

```shell
pip install -r requirements.txt
```

3. Run the server using uvicorn:

```shell
uvicorn server:app
```

4. Run `test_client.py` (because the real client isn't done yet).