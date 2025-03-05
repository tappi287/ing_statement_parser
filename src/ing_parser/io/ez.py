from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

import pandas as pd
from ing_parser.data import BankStatement, Transaction


@dataclass
class EzBookKeepingTransactions:
    time: str
    timezone: str
    type: str
    category: str
    sub_category: str
    account: str
    account_currency: str
    amount: float
    account2: str
    account2_currency: str
    account2_amount: float
    geographic_location: str
    description: str
    tags: List[str] = field(default_factory=list)

    @classmethod
    def from_transaction(cls, transaction: Transaction) -> 'EzBookKeepingTransactions':
        ez_transaction_type = "Income"
        local_now = datetime.now()
        tz_offset = local_now.utcoffset()

        # Format the offset as +HH:MM or -HH:MM
        if tz_offset:
            sign = '+' if tz_offset.days >= 0 else '-'
            hours, remainder = divmod(abs(tz_offset).seconds, 3600)
            minutes = remainder // 60
            timezone_offset = f"{sign}{hours:02}:{minutes:02}"
        else:
            timezone_offset = "+00:00"

        date_obj = datetime.fromisoformat(transaction.date)
        if transaction.amount < 0:
            ez_transaction_type = "Expense"

        desc = transaction.issuer + " " + transaction.description.replace("\n", "; ")
        desc = desc.replace('"', '')

        return cls(
            time=date_obj.strftime("%Y-%m-%d %H:%M:%S"),
            timezone=timezone_offset,
            type=ez_transaction_type,
            category=map_category(transaction.type)[0],
            sub_category=map_category(transaction.type)[1],
            account="ING",
            account_currency="EUR",  # Assuming the currency is EUR; adjust as needed
            amount=abs(transaction.amount),
            account2="",
            account2_currency="",  # Assuming the currency is EUR; adjust as needed
            account2_amount=0.0,
            geographic_location="",
            tags=[],  # Add any relevant tags here
            description=desc
        )

    @classmethod
    def from_bank_statement(cls, bank_statement: BankStatement) -> List['EzBookKeepingTransactions']:
        return [cls.from_transaction(transaction) for transaction in bank_statement.transactions]


def map_category(transaction_type: str) -> Tuple[str, str]:
    type_mapping = {
        "Lastschrift": ("Miscellaneous", "Other Expense"),
        "Entgelt": ("Finance & Insurance", "Service Charge"),
        "Abbuchung": ("Miscellaneous", "Other Income"),
        "Gehalt/Rente": ("Occupational Earnings", "Salary Income"),
        "Gutschrift": ("Miscellaneous", "Other Income"),
        "Retoure": ("Miscellaneous", "Other Income"),
        "Ueberweisung": ("Miscellaneous", "Other Expense"),
        "Dauerauftrag/Terminueberw.": ("Miscellaneous", "Other Expense"),
        # Add more mappings as needed
    }
    return type_mapping.get(transaction_type, ("Miscellaneous", "Other Expense"))


def map_type(transaction_type: str) -> str:
    type_mapping = {
        "Lastschrift": "Expense",
        "Entgelt": "Expense",
        "Abbuchung": "Expense",
        "Gehalt/Rente": "Income",
        "Gutschrift": "Income",
        "Retoure": "Income",
        "Ueberweisung": "Expense",
        "Dauerauftrag/Terminueberw.": "Expense"
        # Add more mappings as needed
    }
    return type_mapping.get(transaction_type, transaction_type)


def convert_to_ez_dataframe(statements: List[BankStatement]) -> pd.DataFrame:
    ez_export_list = []

    for statement in statements:
        ez_export_list.extend(EzBookKeepingTransactions.from_bank_statement(statement))

    # Create a DataFrame from the list of EzBookKeepingExport objects
    return pd.DataFrame([
        {
            "Time": e.time,
            "Timezone": e.timezone,
            "Type": e.type,
            "Category": e.category,
            "Sub Category": e.sub_category,
            "Account": e.account,
            "Account Currency": e.account_currency,
            "Amount": e.amount,
            "Account2": e.account2,
            "Account2 Currency": e.account2_currency,
            "Account2 Amount": e.account2_amount,
            "Geographic Location": e.geographic_location,
            "Tags": ",".join(e.tags),
            "Description": e.description
        }
        for e in ez_export_list
    ])


def export_ez_csv(out_file: Path, df: pd.DataFrame):
    return df.to_csv(out_file, index=False, sep=",", quoting=0, doublequote=False)
