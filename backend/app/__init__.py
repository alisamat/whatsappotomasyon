from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from app.models import db
from app.config.settings import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
    Migrate(app, db)
    CORS(app, resources={r'/api/*': {'origins': '*'}})

    from app.routes import webhook, auth, kredi, admin, panel, belge, emlak_profil, raporlar
    app.register_blueprint(webhook.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(kredi.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(panel.bp)
    app.register_blueprint(belge.bp)
    app.register_blueprint(emlak_profil.bp)
    app.register_blueprint(raporlar.bp)

    @app.route('/health')
    def health():
        return {'status': 'ok'}

    return app
