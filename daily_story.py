from __future__ import annotations

import json
import os
import re

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from flask import request, url_for

from models import Cat
from story_bank import STORY_BANK

try:
    import fcntl
except ImportError:  # Windows does not provide fcntl.
    fcntl = None

MOSCOW_TZ = ZoneInfo("Europe/Moscow")
ADOPTED_STATUS = "Усыновлён"


def clean(value):
    if value is None:
        return ""

    value = str(value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def available_cats():
    return Cat.query.filter(Cat.status != ADOPTED_STATUS).order_by(Cat.id.asc()).all()


def build_story(cat, variant):
    stories = STORY_BANK.get(clean(cat.name).casefold())

    if stories:
        story = stories[variant % len(stories)]
        story = story.replace("\u2014", "-").replace("\u2013", "-").strip()

        return {"text": story, "chips": []}

    name = clean(getattr(cat, "name", "Котик"))
    personality = clean(getattr(cat, "personality", ""))
    description = clean(getattr(cat, "description", ""))
    story_source = clean(getattr(cat, "story", ""))
    activity = clean(getattr(cat, "activity_level", ""))
    variants = []

    if personality:
        variants.append(
            f"Знакомьтесь: {name}. "
            f"В анкете характер описан так: {personality.lower()}. "
            "А при встрече можно узнать побольше о привычках котика и посмотреть, как он общается с людьми."
        )

    if description:
        variants.append(
            f"Сегодня можно поближе познакомиться с котиком по имени {name}. "
            "В анкете есть описание, а сотрудники приюта расскажут о привычках "
            "и помогут подготовиться к первой встрече."
        )

    if story_source:
        variants.append(
            f"{name} попал в Котополис и теперь ждёт знакомства с будущими хозяевами. "
            "О том, как котик оказался в приюте, можно прочитать в анкете. "
            "Если останутся вопросы, задайте их при встрече."
        )

    if activity:
        variants.append(
            f"{name} ждёт знакомства. В анкете указан уровень активности, "
            "чтобы было проще понять, сколько времени понадобится на игры. "
            "Перед встречей можно спросить сотрудников о любимых игрушках котика."
        )

    variants.append(
        f"Котик дня: {name}. "
        "Откройте анкету, посмотрите фотографии и почитайте о привычках. "
        "Если захотите познакомиться, можно отправить заявку."
    )

    story = variants[variant % len(variants)]
    story = story.replace("\u2014", "-").replace("\u2013", "-").strip()

    return {"text": story, "chips": []}


def state_paths(app):
    directory = Path(
        app.config.get("STORY_STATE_DIR", str(Path(app.root_path) / "data"))
    )

    directory.mkdir(parents=True, exist_ok=True)

    return (directory / "daily_story_state.json", directory / "daily_story_state.lock")


def read_state(path):
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))

        if (
            isinstance(data, dict)
            and isinstance(data.get("cycle_shown", []), list)
            and isinstance(data.get("variants", {}), dict)
            and isinstance(data.get("text", ""), str)
            and isinstance(data.get("cat_id", 0), int)
        ):
            return data

    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}

    return {}


def write_state(path, state):
    temp = Path(str(path) + ".tmp")

    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    os.replace(temp, path)


def choose_story(app):
    cats = available_cats()

    if not cats:
        return None

    by_id = {cat.id: cat for cat in cats}
    state_path, lock_path = state_paths(app)
    today = datetime.now(MOSCOW_TZ).date().isoformat()

    with lock_path.open("a+", encoding="utf-8") as lock:
        if fcntl is not None:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

        state = read_state(state_path)
        current_id = state.get("cat_id")

        if state.get("date") == today and current_id in by_id and state.get("text"):
            cat = by_id[current_id]

            return format_result(cat, state.get("text", ""), state.get("chips", []))

        eligible_ids = set(by_id.keys())
        shown = []

        for value in state.get("cycle_shown", []):
            try:
                value = int(value)

            except (TypeError, ValueError):
                continue

            if value in eligible_ids:
                shown.append(value)

        remaining = [cat for cat in cats if cat.id not in shown]

        if not remaining:
            shown = []
            remaining = list(cats)

        # При одинаковом состоянии разные workers выберут одного котика.
        day_number = datetime.now(MOSCOW_TZ).date().toordinal()
        index = day_number % len(remaining)
        cat = remaining[index]
        variants = state.get("variants", {})
        if not isinstance(variants, dict):
            variants = {}

        try:
            variant = int(variants.get(str(cat.id), 0))

        except (TypeError, ValueError):
            variant = 0

        story = build_story(cat, variant)
        variants[str(cat.id)] = variant + 1

        shown.append(cat.id)

        new_state = {
            "date": today,
            "cat_id": cat.id,
            "cycle_shown": shown,
            "variants": variants,
            "text": story["text"],
            "chips": story["chips"],
        }

        write_state(state_path, new_state)

        return format_result(cat, story["text"], story["chips"])


def format_result(cat, text, chips):
    photo_path = clean(getattr(cat, "photo_path", None))

    if photo_path:
        if photo_path.startswith("http://") or photo_path.startswith("https://"):
            photo_url = photo_path

        else:
            photo_url = url_for("static", filename=photo_path)

    else:
        photo_url = None

    return {"cat": cat, "text": text, "chips": chips, "photo_url": photo_url}


def register_daily_story(app):
    @app.context_processor
    def inject_daily_story():
        if request.endpoint != "dashboard":
            return {}

        return {"daily_story": choose_story(app)}
