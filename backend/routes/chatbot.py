from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required

from services.chatbot_service import get_reply

bp = Blueprint("chatbot", __name__, url_prefix="/api/chatbot")


@bp.post("/message")
@jwt_required()
def message():
    data = request.get_json(force=True) or {}
    text = data.get("message", "")
    if not text.strip():
        return jsonify({"error": "validation_error", "message": "message is required."}), 400
    result = get_reply(text)
    return jsonify(result)
