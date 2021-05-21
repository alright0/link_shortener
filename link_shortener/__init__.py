from pathlib import Path

import sqlalchemy as db
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask import Flask
from flask_apispec.extension import FlaskApiSpec
from flask_swagger_ui import get_swaggerui_blueprint
from hashids import Hashids
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

path = Path(__file__).parents[0]

app = Flask(__name__)

app.config["SECRET_KEY"] = "SECRET KEY"

client = app.test_client()

hashid = Hashids(min_length=4, salt=app.config["SECRET_KEY"])

engine = create_engine(f"sqlite:///{path}\database.db")
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

docs = FlaskApiSpec()
app.config.update(
    {
        "APISPEC_SPEC": APISpec(
            title="link_shortener",
            version="v1",
            openapi_version="3.0.2",
            plugins=[MarshmallowPlugin()],
        ),
        "APISPEC_SWAGGER_URL": "/docs/",
    }
)

from flask_swagger_ui import get_swaggerui_blueprint

SWAGGER_URL = "/index/"
API_URL = "/docs/"

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "My App"}
)

from link_shortener.models import *

Base.metadata.create_all(bind=engine)


from link_shortener.handlers.handlers import error_handlers
from link_shortener.views.views import *

app.register_blueprint(error_handlers)
app.register_blueprint(shortener_api)
app.register_blueprint(swagger_ui_blueprint)

docs.init_app(app)
