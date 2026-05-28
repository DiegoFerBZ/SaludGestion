from datetime import datetime, timezone

from flask import jsonify


def api_response(success=True, data=None, status_code=200):
    payload = {
        "success": success,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return jsonify(payload), status_code
