import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from models import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": [app.config["FRONTEND_URL"], "*"]}})
    JWTManager(app)
    db.init_app(app)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ---- Blueprints ----
    from routes import auth, candidates, positions, applications, screening, analytics, chatbot, reports
    app.register_blueprint(auth.bp)
    app.register_blueprint(candidates.bp)
    app.register_blueprint(positions.bp)
    app.register_blueprint(applications.bp)
    app.register_blueprint(screening.bp)
    app.register_blueprint(analytics.bp)
    app.register_blueprint(chatbot.bp)
    app.register_blueprint(reports.bp)

    @app.get("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "db_engine": app.config["DB_ENGINE_NAME"],
            "product": "TalentIQ: AI-Powered Recruitment Intelligence",
        })

    @app.errorhandler(404)
    def not_found(_):
        return jsonify({"error": "not_found", "message": "The requested resource was not found."}), 404

    @app.errorhandler(500)
    def server_error(exc):
        return jsonify({"error": "server_error", "message": "Something went wrong. Please try again."}), 500

    with app.app_context():
        db.create_all()
        _maybe_seed()

    return app


def _maybe_seed():
    """Auto-seeds demo data on first run against an empty database."""
    from models import User
    if User.query.first() is None:
        try:
            from database.seed import run_seed
            run_seed()
            print("[TalentIQ] Database was empty — seeded with demo data.")
        except Exception as exc:  # noqa: BLE001
            print(f"[TalentIQ] Auto-seed skipped: {exc}")


# Module-level app object so production servers (gunicorn, Render, etc.)
# can import it directly as `app:app`.
app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
