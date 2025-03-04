import re

from ing_parser.data import BankStatement


class IngBase:
    # Not in use
    _TYPES = (
    "lastschrift", "ueberweisung", "entgelt", "dauerauftrag/terminueberw.", "gehalt/rente", "gutschrift", "abbuchung",
    "retoure")

    _SEARCH_TERM = "kontoauszug"
    _MAX_DESC_LINES = 3
    _DATE_REGEX = re.compile(r"^(0[1-9]|[12]\d|3[01])[.](0[1-9]|1[012])[.](19|20)(\d{2})")
    _AMOUNT_REGEX = re.compile(r"(-?(\d{1,3}(\.\d{3})*|\d+),\d{2})$")

    @staticmethod
    def _parse_statement_fields(line: str, statement: 'BankStatement'):
        for field_name, regex in statement.get_regex_fields().items():
            m = re.match(regex, line)
            if m:
                statement.set_field_from_regex(field_name, m)
