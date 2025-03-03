import locale
import logging
import re
from datetime import datetime
from typing import Optional

try:
    # Try to set locale to german for parsing german date description
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
except Exception as e:
    logging.error(e)


class IngBase:
    # Not in use
    _TYPES = (
    "lastschrift", "ueberweisung", "entgelt", "dauerauftrag/terminueberw.", "gehalt/rente", "gutschrift", "abbuchung",
    "retoure")

    _SEARCH_TERM = "kontoauszug"
    _MAX_DESC_LINES = 3
    _DATE_REGEX = re.compile(r"^(0[1-9]|[12]\d|3[01])[.](0[1-9]|1[012])[.](19|20)(\d{2})")
    _AMOUNT_REGEX = re.compile(r"(-?(\d{1,3}(\.\d{3})*|\d+),\d{2})$")

    _STATEMENT_MONTH_REGEX = re.compile(r"^Kontoauszug\s([A-Za-z]+)\s(\d{4})$")
    _STATEMENT_DATE_REGEX = re.compile(r"^Datum\s(\d{2}\.\d{2}\.\d{4})$")
    _STATEMENT_NUMBER_REGEX = re.compile(r"^Auszugsnummer\s([0-9]{1,2})$")
    _STATEMENT_BALANCE_REGEX = re.compile(r"^Neuer\sSaldo\s(-?\d+\.?\d*),(\d{1,2})\sEuro$")
    _STATEMENT_BALANCE_OLD_REGEX = re.compile(r"^Alter\sSaldo\s(-?\d+\.?\d*),(\d{1,2})\sEuro$")
    _STATEMENT_IBAN_REGEX = re.compile(r'^IBAN\s([A-Z]{2}\d{2}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{2})$')
    _STATEMENT_BIC_REGEX = re.compile(r'^BIC\s([A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?)$')

    def _parse_statement_balance(self, line: str) -> Optional[float]:
        m = re.match(self._STATEMENT_BALANCE_REGEX, line)
        return float(f"{m.group(1).replace('.', '')}.{m.group(2)}") if m else None

    def _parse_statement_balance_old(self, line: str) -> Optional[float]:
        m = re.match(self._STATEMENT_BALANCE_OLD_REGEX, line)
        return float(f"{m.group(1).replace('.', '')}.{m.group(2)}") if m else None

    def _parse_statement_month(self, line: str) -> Optional[datetime]:
        m = re.match(self._STATEMENT_MONTH_REGEX, line)
        return datetime.strptime(f"{m.group(1)} {m.group(2)}", "%B %Y") if m else None

    def _parse_statement_date(self, line: str) -> Optional[datetime]:
        m = re.match(self._STATEMENT_DATE_REGEX, line)
        return datetime.strptime(f"{m.group(1)}", "%d.%m.%Y") if m else None

    def _parse_statement_number(self, line: str) -> Optional[int]:
        m = re.match(self._STATEMENT_NUMBER_REGEX, line)
        return int(m.group(1)) if m else None

    def _parse_statement_iban(self, line: str) -> Optional[str]:
        m = re.match(self._STATEMENT_IBAN_REGEX, line)
        return m.group(1).replace(" ", "") if m else None

    def _parse_statement_bic(self, line: str) -> Optional[str]:
        m = re.match(self._STATEMENT_BIC_REGEX, line)
        return m.group(1) if m else None

    def _to_iso_date(self, date: str) -> str:
        return datetime.strptime(date, "%d.%m.%Y").isoformat()
