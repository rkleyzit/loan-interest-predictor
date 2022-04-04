import uvicorn
from fastapi import FastAPI

from register_routes import register_routes
from utils import database


def init_app():
    api = FastAPI()
    database.init_db()

    return register_routes(api)


app = init_app()

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)
