"""AIML-like template engine backed by aiml_categories table.

Per PRD Section 3.3 / 20.2.
"""
import re
from typing import Optional
from sqlalchemy.orm import Session as DBSession

from app.models.aiml_category import AIMLCategory


PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z0-9_]+)\}")


class AIMLInterpreter:
    def __init__(self, db: DBSession):
        self.db = db

    def _find(self, pattern: str, topic: Optional[str] = None, that_pattern: Optional[str] = None) -> Optional[AIMLCategory]:
        q = self.db.query(AIMLCategory).filter(
            AIMLCategory.pattern == pattern,
            AIMLCategory.is_active.is_(True),
        )
        if topic:
            cat = q.filter(AIMLCategory.topic == topic).first()
            if cat:
                return cat
        if that_pattern:
            cat = q.filter(AIMLCategory.that_pattern == that_pattern).first()
            if cat:
                return cat
        return q.first()

    @staticmethod
    def _render_template(template: str, context: dict) -> str:
        def replace(match: re.Match) -> str:
            key = match.group(1)
            return str(context.get(key, match.group(0)))
        return PLACEHOLDER_RE.sub(replace, template)

    @staticmethod
    def _render_quick_replies(quick_replies: Optional[list], context: dict) -> Optional[list]:
        if not quick_replies:
            return None
        rendered = []
        for qr in quick_replies:
            new_qr = dict(qr)
            if "label" in new_qr:
                new_qr["label"] = AIMLInterpreter._render_template(new_qr["label"], context)
            rendered.append(new_qr)
        return rendered

    def respond(self, pattern: str, context: Optional[dict] = None, topic: Optional[str] = None,
                that_pattern: Optional[str] = None) -> dict:
        context = context or {}
        cat = self._find(pattern, topic=topic, that_pattern=that_pattern)
        if not cat:
            fallback = self._find("NOT_UNDERSTOOD")
            if fallback:
                return {
                    "pattern": "NOT_UNDERSTOOD",
                    "aiml_category_id": fallback.id,
                    "message": self._render_template(fallback.template, context),
                    "quick_replies": self._render_quick_replies(fallback.quick_replies, context),
                }
            return {
                "pattern": pattern,
                "aiml_category_id": None,
                "message": "Maaf, saya belum memahami permintaan Anda.",
                "quick_replies": None,
            }
        return {
            "pattern": cat.pattern,
            "aiml_category_id": cat.id,
            "message": self._render_template(cat.template, context),
            "quick_replies": self._render_quick_replies(cat.quick_replies, context),
        }
