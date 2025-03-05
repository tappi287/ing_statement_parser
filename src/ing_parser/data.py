import locale
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

try:
    # Try to set locale to german for parsing german date description
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
except Exception as e:
    logging.error(e)


def to_iso_date(date: str) -> str:
    return datetime.strptime(date, "%d.%m.%Y").isoformat()


def parse_statement_month(v: Optional[re.Match]) -> Optional[datetime]:
    if len(v.groups()) != 2:
        return None
    return datetime.strptime(f"{v.group(1)} {v.group(2)}", "%B %Y") if v else None


def parse_statement_date(v: Optional[re.Match]) -> Optional[datetime]:
    if len(v.group(1)) != 10:
        return None
    return datetime.strptime(f"{v.group(1)}", "%d.%m.%Y") if v else None


def parse_float(v: Optional[re.Match]) -> Optional[float]:
    if len(v.groups()) != 1:
        return None
    return float(v.group(1).replace(".", "").replace(",", "."))


@dataclass
class Transaction:
    date: str
    valuta: str
    issuer: str
    type: str
    description: str
    amount: float


_STATEMENT_MONTH_REGEX = re.compile(r"^Kontoauszug\s([A-Za-z]+)\s(\d{4})$")
_STATEMENT_DATE_REGEX = re.compile(r"^Datum\s(\d{2}\.\d{2}\.\d{4})$")
_STATEMENT_NUMBER_REGEX = re.compile(r"^Auszugsnummer\s([0-9]{1,2})$")
_STATEMENT_BALANCE_REGEX = re.compile(r"^Neuer\sSaldo\s(-?\d+\.?\d*,\d{1,2})\sEuro$")
_STATEMENT_BALANCE_OLD_REGEX = re.compile(r"^Alter\sSaldo\s(-?\d+\.?\d*,\d{1,2})\sEuro$")
_STATEMENT_IBAN_REGEX = re.compile(r'^IBAN\s([A-Z]{2}\d{2}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{2})$')
_STATEMENT_BIC_REGEX = re.compile(r'^BIC\s([A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?)$')


@dataclass
class BankStatement:
    statement_number: int = 0
    statement_date: str = ""
    statement_month: int = 0
    statement_year: int = 0
    statement_balance: float = 0.0
    statement_old_balance: float = 0.0
    transactions: List[Transaction] = field(default_factory=list)
    account_id: str = str()
    bank_id: str = str()

    _FIELDS = {
        'statement_number': _STATEMENT_NUMBER_REGEX,
        'statement_date': _STATEMENT_DATE_REGEX,
        'statement_month': _STATEMENT_MONTH_REGEX,
        'statement_year': _STATEMENT_MONTH_REGEX,
        'statement_balance': _STATEMENT_BALANCE_REGEX,
        'statement_old_balance': _STATEMENT_BALANCE_OLD_REGEX,
        'account_id': _STATEMENT_IBAN_REGEX,
        'bank_id': _STATEMENT_BIC_REGEX
    }

    def get_regex_fields(self):
        return self._FIELDS

    def set_field_from_regex(self, field_name: str, value: re.Match):
        match field_name:
            case 'statement_number':
                value = int(value.group(1)) if value.group(1).isdigit() else value
            case 'statement_date':
                date = parse_statement_date(value)
                value = date.isoformat() if date else value
            case 'statement_month':
                date = parse_statement_month(value)
                value = date.month if date else value
            case 'statement_year':
                date = parse_statement_month(value)
                value = date.year if date else value
            case 'statement_balance':
                value = parse_float(value) if parse_float(value) else value
            case 'statement_old_balance':
                value = parse_float(value) if parse_float(value) else value
            case 'account_id':
                value = value.group(1).replace(" ", "")
            case _:
                value = value.group(1)

        setattr(self, field_name, value)

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def clear_transactions(self):
        self.transactions = list()

    def __str__(self):
        statement_header = (f"Kontoauszug {self.statement_month} {self.statement_year} "
                            f"Auszugsnummer {self.statement_number}, {self.statement_date}")
        transaction_details = "\n".join(
            f"Buchung {t.date[:10]}, Valuta {t.valuta[:10]}, {t.issuer}, {t.type}, {t.amount:.2f}" for t in
            self.transactions)
        return f"{statement_header}\n{transaction_details}"
