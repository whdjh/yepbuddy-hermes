from __future__ import annotations

from telegram import Update


def actor_id(update: Update) -> int | None:
    user = update.effective_user
    return user.id if user else None


def is_authorized(update: Update, allowed_user_ids: frozenset[int]) -> bool:
    user_id = actor_id(update)
    return user_id is not None and user_id in allowed_user_ids
