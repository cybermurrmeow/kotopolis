from io import StringIO

from models import Cat
from utils import export_to_csv, spreadsheet_safe


def test_spreadsheet_formula_injection_is_escaped():
    assert spreadsheet_safe('=HYPERLINK("https://example.test")').startswith("'")
    assert spreadsheet_safe("Обычный текст") == "Обычный текст"


def test_csv_export_escapes_formula_like_cat_data():
    content = export_to_csv([Cat(id=1, name="=1+1", status="В приюте")])
    text = StringIO(content).read()

    assert "'=1+1" in text
