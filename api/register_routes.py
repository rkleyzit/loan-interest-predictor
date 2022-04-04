import importlib
import os
from pathlib import Path
from fastapi import FastAPI


def register_routes(app: FastAPI) -> FastAPI:
    path = 'routes'
    here = Path(__file__).parent.joinpath(path)
    routes = os.listdir(here)

    for route in routes:
        api = importlib.import_module(f"{path}.{route.split('.')[0]}")
        if hasattr(api, 'router'):
            prefix = '/api' + ('' if not hasattr(api, 'prefix') else api.prefix)
            app.include_router(api.router, prefix=prefix)

    return app
