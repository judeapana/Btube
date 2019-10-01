from Btube.api.routes import api


class BlueprintUrl:
    def __init__(self, app):
        app.register_blueprint(api, url_prefix='/api')
