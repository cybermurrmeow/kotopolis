from pathlib import Path
import re

from daily_story import build_story
from models import Cat
from story_bank import STORY_BANK


ROOT = Path(__file__).resolve().parents[1]
LONG_DASHES = {chr(code) for code in range(0x2012, 0x2016)}
DASH_ENTITY = re.compile(r"&(?:mdash|ndash|#(?:821[0123]|x201[2345]));", re.IGNORECASE)
TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".html",
    ".css",
    ".js",
    ".svg",
    ".txt",
    ".toml",
    ".yml",
    ".yaml",
    ".ini",
    ".mako",
    ".example",
}


def test_source_text_has_no_long_dashes():
    files = {path for path in ROOT.iterdir() if path.is_file()}
    for directory in (
        "docs",
        "templates",
        "checks",
        "tests",
        "migrations",
        "static/js",
        "static/css",
        "static/img",
    ):
        files.update(path for path in (ROOT / directory).rglob("*") if path.is_file())
    for path in sorted(files):
        if path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        assert not LONG_DASHES.intersection(text), path.relative_to(ROOT)
        assert not DASH_ENTITY.search(text), path.relative_to(ROOT)


def test_all_story_variants_replace_long_dashes():
    for name, variants in STORY_BANK.items():
        cat = Cat(name=name)
        for index in range(len(variants)):
            assert not LONG_DASHES.intersection(build_story(cat, index)["text"])
    cat = Cat(
        name="Тест" + chr(0x2014) + "кот",
        personality="Спокойный" + chr(0x2013) + "ласковый",
        description="Описание",
        story="История",
        activity_level="Низкий",
    )
    for index in range(5):
        assert not LONG_DASHES.intersection(build_story(cat, index)["text"])
