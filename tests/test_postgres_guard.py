import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "checks"))
from postgres_review import validate_url  # noqa: E402


@pytest.mark.parametrize(
    "url",
    [
        "postgresql://localhost/kotopolis",
        "postgresql://meowly.space/kotopolis_review",
        "postgresql://localhost/kotopolis_review?options=-csearch_path=public",
        "sqlite:///kotopolis_review",
    ],
)
def test_postgres_check_rejects_unsafe_targets(url):
    with pytest.raises(ValueError):
        validate_url(url)


def test_postgres_check_accepts_local_review_database():
    assert (
        validate_url("postgresql://localhost/kotopolis_review").database
        == "kotopolis_review"
    )
