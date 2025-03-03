from dataclasses import dataclass, field
from typing import List


@dataclass
class Transaction:
    date: str
    valuta: str
    issuer: str
    type: str
    description: str
    amount: float


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

    def add_transaction(self, transaction: Transaction):
        self.transactions.append(transaction)

    def clear_transactions(self):
        self.transactions = list()

    def __str__(self):
        statement_header = (f"Kontoauszug {self.statement_month} {self.statement_year} "
                            f"Auszugsnummer {self.statement_number}, {self.statement_date}")
        transaction_details = "\n".join(
            f"Buchung {t.date[:10]}, Valuta {t.valuta[:10]}, {t.issuer}, {t.type}, {t.amount:.2f}"
            for t in self.transactions
        )
        return f"{statement_header}\n{transaction_details}"
