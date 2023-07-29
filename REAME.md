# DRF-channels based messanger api.

Here I practice `djangochannelsresrframework` library for other big projects. I have some ideas and practices to do
to optimize API application.

*NOTE*: server root is project root;

## Stack
- `Python 3.11`;
- `Django`;
- `Django Rest Framework`;
- `djangochannelsresrframework`;
- `redis`;
- `Docker`;

## Requirements
I use `Python 3.11` as the project language.

You can install application requirements with:
```commandline
pip install -r requirements.txt
```

or write this for more information:
```commandline
pytest -s -vv
```


## Running application
You can run it using `Docker`. Run this command in the project root directory.

The server is default running at `localhost:8008`.

```commandline
docker-compose up -d --build
```

For local running using `uvicorn` run:
```commandline
python manage.py makemigrations
python manage.py migrate
python mange.py runserver
```
