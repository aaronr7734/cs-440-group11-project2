"""
This module implements view handling and template rendering for web pages.
It provides utility functions for manipulating HTML templates and adding
dynamic client-side behaviors.

Classes:
    ViewHandler: Manages template rendering and HTML manipulation operations
"""

from typing import Dict, Any
from flask import render_template


class ViewHandler:
    @staticmethod
    def render_with_context(template_name: str, **context) -> str:
        """Render template with given context"""
        return render_template(template_name, **context)

    @staticmethod
    def inject_book_id(template: str, book_id: str) -> str:
        """Inject book ID into template"""
        return template.replace("BOOKID", book_id)

    @staticmethod
    def add_alert_script(html: str, message: str) -> str:
        """Add JavaScript alert to HTML"""
        return html + f'<script>alert("{message}");</script>'

    @staticmethod
    def add_redirect_script(html: str, url: str) -> str:
        """Add JavaScript redirect to HTML"""
        return html + f'<script>window.location.href="{url}";</script>'
