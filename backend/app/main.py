import sys
import os
from werkzeug.exceptions import HTTPException, BadRequest
from flask import Flask, jsonify, session  # pyright: ignore[reportMissingImports]
from flask_cors import CORS  # pyright: ignore[reportMissingModuleSource]
from flask_migrate import Migrate
from extensions import redis_client
from core.config import init_db
from dotenv import load_dotenv
from flasgger import Swagger

from extensions import db, redis_client, mail_service

from api.v1.endpoints.ep_auth import auth
from api.v1.endpoints.ep_user import user
from api.v1.endpoints.ep_admin import admin
from core.event import trigger_achievement_dispatch

load_dotenv()

bp_list = [auth, user, admin]

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def register_error_handlers(app):
    @app.errorhandler(Exception)
    def handle_global_exception(e):
        if isinstance(e, HTTPException):
            error_content = e.description if hasattr(e, 'description') else str(e)
            if isinstance(error_content, str) and "|" in error_content:
                slug, message = error_content.split("|", 1)
            else:
                slug = "BAD_REQUEST"
                message = error_content if isinstance(error_content, str) else "Une validation de données a échoué."
            return jsonify({
                "status": "error", 
                "slug": slug,
                "message": message
            }), e.code
        app.logger.error(f"⚠️ CRASH CRITIQUE : {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "slug": "INTERNAL_SERVER_ERROR",
            "message": "Une erreur interne imprévue est survenue."
        }), 500

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('FLASK_SECRET_KEY')
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guardihack.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SMTP_SERVER'] = os.getenv('SMTP_SERVER')
    app.config['SMTP_USERNAME'] = os.getenv('SMTP_USERNAME')
    app.config['SMTP_PASSWORD'] = os.getenv('SMTP_PASSWORD')
    app.config['MAIL_SENDER'] = os.getenv('MAIL_SENDER')
    CORS(app, supports_credentials=True)
    app.config['SWAGGER'] = {
        'openapi': '3.0.0',
        'title': 'GuardiHack API v1',
        'uiversion': 3,
        'ui_params': {
            'withCredentials': True
        }
    }
    mail_service.init_app(app)
    db.init_app(app)
    swagger = Swagger(app)
    with app.app_context():
        if not os.path.exists(db_path):
            print("Base de données non trouvée. Initialisation en cours...")
            db.create_all()
            init_db()
    for bp in bp_list:
        app.register_blueprint(bp)
    register_error_handlers(app)
    @app.before_request
    def track_user_online():
        user_id = session.get('user_id')
        if user_id:
            redis_client.setex(f"online_user:{user_id}", 300, "1")
    migrate = Migrate(app, db)
    return app
app = create_app()

@app.route('/')
def home():
    return {"status": "Server is running", "project": "GuardiHack v1"}



if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=9414)

