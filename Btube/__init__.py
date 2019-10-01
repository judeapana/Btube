from flask import Flask
from Btube.urls import BlueprintUrl
from Btube.config import LocalConfig

app = Flask(__name__)


def create_app(Config=LocalConfig):
    app.config.from_object(Config)
    BlueprintUrl(app)
    return app
