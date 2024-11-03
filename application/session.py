"""
This module implements session management functionality for user authentication
and state persistence. It serves as a wrapper around Flask's session object to
provide structured access to session data.

Classes:
    SessionManager: Handles session creation and management operations
"""

from typing import Optional, Dict
from flask import session


class SessionManager:
    @staticmethod
    def create_session(user_id: int, username: str, email: str) -> None:
        session["user_id"] = user_id
        session["user_name"] = username
        session["user_email"] = email

    @staticmethod
    def clear_session() -> None:
        session.clear()

    @staticmethod
    def get_user_id() -> Optional[int]:
        return session.get("user_id")

    @staticmethod
    def get_user_data() -> Optional[Dict]:
        if "user_id" in session:
            return {
                "id": session["user_id"],
                "username": session["user_name"],
                "email": session["user_email"],
            }
        return None

    @staticmethod
    def is_authenticated() -> bool:
        return "user_email" in session
