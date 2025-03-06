import logging
from pathlib import Path
from typing import Union, List

import pandas as pd
from pypdf import PdfReader

from ing_parser.base import IngBase
from ing_parser.data import BankStatement, Transaction, to_iso_date


class IngStatement(IngBase, BankStatement):

    def __init__(self, source_file: Union[str, Path]):
        """
        Parses a given bank statement PDF file and returns its contents as a pandas DataFrame.

        dataframe:
            pd.DataFrame: A DataFrame containing the parsed data from the bank statement PDF file.

            The DataFrame has six columns:
                'date' (datetime), 'valuta' (datetime), 'issuer' (str), 'type' (str)
                'description' (str), and 'amount' (float).
        """
        super().__init__()
        self.source_file = Path(source_file)
        self._rows = dict()
        self._parsed = False

    def _to_pandas_df(self) -> pd.DataFrame:
        """Create a Pandas DataFrame from the BankStatement Transaction data."""
        transactions_data = []
        for transaction in self.transactions:
            date_str = pd.to_datetime(transaction.date)
            valuta_str = pd.to_datetime(transaction.valuta)
            issuer_str = transaction.issuer
            type_str = transaction.type
            description_str = transaction.description
            amount = transaction.amount

            transactions_data.append([date_str, valuta_str, issuer_str, type_str, description_str, amount])

        # Convert list of lists to DataFrame
        return pd.DataFrame(transactions_data, columns=['date', 'valuta', 'issuer', 'type', 'description', 'amount'])

    @property
    def dataframe(self) -> pd.DataFrame:
        if not len(self.transactions):
            self._auto_parse_ing_bank_statement()
        return self._to_pandas_df()

    def _auto_parse_ing_bank_statement(self):
        """ Meant to not reparse on every call to properties """
        if self._parsed:
            return
        self._parsed = True
        self.parse_ing_bank_statement()

    def parse_ing_bank_statement(self):
        self.clear_transactions()
        self._rows = {"date": [], "valuta": [], "issuer": [], "type": [], "description": [], "amount": []}

        skip_next_line = False
        lines = self._read_pdf()

        for idx, line in enumerate(lines):
            self._parse_statement_fields(line, self)
            if skip_next_line:
                skip_next_line = False
                continue

            if self._parse_transaction_line(line):
                # -- Did the previous line contained a valid entry
                #    then read the following line with transaction description
                self._parse_description(lines, idx)
                skip_next_line = True

        # -- Store transactions data
        for idx in range(len(self._rows['date'])):
            data = {k: v[idx] for k, v in self._rows.items()}
            self.add_transaction(Transaction(**data))

    def _read_pdf(self) -> List[str]:
        lines = list()
        try:
            reader = PdfReader(self.source_file)
        except Exception as e:
            logging.error(f"Error reading file while trying to parse statement: {e}")
            return lines

        for page in reader.pages:
            content = page.extract_text(0)
            lines += content.split("\n")

        return lines

    def _parse_transaction_line(self, line: str) -> bool:
        """ Parse data belonging to transactions """
        amount = self._AMOUNT_REGEX.search(line)
        if amount is None:
            return False

        date = self._DATE_REGEX.search(line)
        if date is None:
            return False

        date_string = date.group(0)
        amount = amount.group(0)
        line_wo_date = line[len(date_string): -len(amount)].strip()

        tr_type = line_wo_date[:line_wo_date.find(" ") if line_wo_date.find(" ") > -1 else 0]
        issuer = line_wo_date[len(tr_type):].strip()

        amount = float(amount.replace(".", "").replace(",", "."))
        self._rows["date"].append(to_iso_date(date_string))
        self._rows["amount"].append(amount)
        self._rows["issuer"].append(issuer)
        self._rows["type"].append(tr_type)

        # The following line belongs to this entry
        return True

    def _parse_description(self, lines, current_idx):
        # -- Parse first description line including Valuta
        self._parse_first_description_line(lines[current_idx + 1])

        # -- Parse additional description lines
        for idx, line in enumerate(lines[current_idx + 2:]):
            date = self._DATE_REGEX.search(line)
            # -- Date found, new entry, abort
            if date is not None or idx >= self._MAX_DESC_LINES:
                return
            self._rows["description"][-1] += "\n" + line.strip()

    def _parse_first_description_line(self, line):
        valuta = self._DATE_REGEX.search(line)
        if valuta is not None:
            valuta = valuta.group(0)
            description = line[len(valuta):].strip()
            self._rows["valuta"].append(to_iso_date(valuta))
            self._rows["description"].append(description)
