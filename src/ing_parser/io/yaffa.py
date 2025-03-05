from dataclasses import dataclass, field
from typing import List

import pandas as pd

from ing_parser.data import BankStatement


@dataclass
class YaffaTransaction:
    date: str
    valuta: str
    account_from: str  # Changed from issuer to account_from
    type: str
    org_type: str
    category: str # Added for Yaffa
    comment: str  # Changed from description to comment
    amount: float
    account_to: str = ""  # Added new field


def map_type(transaction_type: str) -> str:
    type_mapping = {
        "Lastschrift": "Withdraw",
        "Entgelt": "Withdraw",
        "Abbuchung": "Withdraw",
        "Gehalt/Rente": "Deposit",
        "Gutschrift": "Deposit",
        "Retoure": "Deposit",
        "Ueberweisung": "Transfer",
        "Dauerauftrag/Terminueberw.": "Scheduled"
        # Add more mappings as needed
    }
    return type_mapping.get(transaction_type, transaction_type)


@dataclass
class YaffaBankStatement:
    statement_number: int = 0
    statement_date: str = ""
    statement_month: int = 0
    statement_year: int = 0
    statement_balance: float = 0.0
    statement_old_balance: float = 0.0
    transactions: List[YaffaTransaction] = field(default_factory=list)
    account_id: str = str()
    bank_id: str = str()

    @classmethod
    def from_statement(cls, statement: BankStatement) -> 'YaffaBankStatement':
        yf = YaffaBankStatement()
        yf.convert_to_yaffa(statement)
        return yf

    @property
    def dataframe(self) -> pd.DataFrame:
        return self.to_dataframe()

    def convert_to_yaffa(self, bank_statement: BankStatement):
        self.statement_number = bank_statement.statement_number
        self.statement_date = bank_statement.statement_date
        self.statement_month = bank_statement.statement_month
        self.statement_year = bank_statement.statement_year
        self.statement_balance = bank_statement.statement_balance
        self.statement_old_balance = bank_statement.statement_old_balance

        # Convert transactions
        for transaction in bank_statement.transactions:
            new_transaction = YaffaTransaction(
                date=transaction.date,
                valuta=transaction.valuta,
                account_from=transaction.issuer,  # Changed from issuer to account_from
                type=map_type(transaction.type),
                org_type=transaction.type,
                category=str(),
                comment=transaction.description,  # Changed from description to comment
                amount=abs(transaction.amount),
                account_to=bank_statement.account_id  # Always set BankStatement.account_id in that field
            )
            self.transactions.append(new_transaction)

        self.account_id = bank_statement.account_id
        self.bank_id = bank_statement.bank_id


    def to_dataframe(self) -> pd.DataFrame:
        # Create a list of dictionaries from the transactions
        transaction_list = [
            {
                "date": transaction.date,
                "valuta": transaction.valuta,
                "account_from": transaction.account_from,
                "type": transaction.type,
                "category": transaction.category,
                "comment": transaction.comment,
                "amount": transaction.amount,
                "account_to": transaction.account_to
            }
            for transaction in self.transactions
        ]

        # Convert the list of dictionaries to a DataFrame
        return pd.DataFrame(transaction_list)


def convert_to_yaffa(statements: List[BankStatement]) -> List[YaffaBankStatement]:
    return [convert_statement_to_yaffa(s) for s in statements]


def convert_statement_to_yaffa(statement: BankStatement) -> YaffaBankStatement:
    return YaffaBankStatement.from_statement(statement)
