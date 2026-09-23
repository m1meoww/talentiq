from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt

from models import db, User, CandidateProfile

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    data = request.get_json(force=True) or {}
    name, email, password = data.get("name"), data.get("email"), data.get("password")
    role = data.get("role", "Candidate")

    if not all([name, email, password]):
        return jsonify({"error": "validation_error", "message": "name, email and password are required."}), 400
    if role not in ("Admin", "HR", "Candidate"):
        role = "Candidate"
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_taken", "message": "An account with this email already exists."}), 409

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()

    if role == "Candidate":
        db.session.add(CandidateProfile(user_id=user.id))

    db.session.commit()

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"token": token, "user": user.to_dict()}), 201


@bp.post("/login")
def login():
    data = request.get_json(force=True) or {}
    email, password = data.get("email"), data.get("password")
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password or ""):
        return jsonify({"error": "invalid_credentials", "message": "Incorrect email or password."}), 401

    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify({"token": token, "user": user.to_dict()})


@bp.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "not_found"}), 404
    return jsonify({"user": user.to_dict()})


@bp.post("/forgot-password")
def forgot_password():
    # Demo-safe stub: never reveal whether an email exists.
    return jsonify({"message": "If that email exists in our system, a reset link has been sent."})
