"""
This module implements standardized response formatting for API endpoints and
web interfaces. It provides consistent structure for success responses,
error handling, and redirects.

Classes:
    ResponseFormatter: Handles response formatting and standardization
"""

from typing import Any, Dict, Optional
from flask import jsonify, redirect


class ResponseFormatter:
    @staticmethod
    def success(data: Any = None, message: str = "") -> Dict:
        return jsonify({"status": "success", "data": data, "message": message})

    @staticmethod
    def error(message: str, code: int = 400) -> Dict:
        return jsonify({"status": "error", "message": message}), code

    @staticmethod
    def redirect_with_message(url: Optional[str], message: Optional[str] = None) -> str:
        if url is None:
            # Use JavaScript to go back to previous page
            return f'<script>alert("{message}");history.go(-1);</script>'
        elif message:
            return f'<script>alert("{message}");window.location.href="{url}";</script>'
        return redirect(url)

    @staticmethod
    def json_message(message: str) -> str:
        return jsonify({"message": message})
