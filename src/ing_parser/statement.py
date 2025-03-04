from pathlib import Path
from typing import Union, Optional, List

import pandas as pd
from pypdf import PdfReader

from ing_parser.base import IngBase
from ing_parser.data import BankStatement, Transaction, to_iso_date


class IngStatement(IngBase):
    def __init__(self, source_file: Union[str, Path]):
        """
        Parses a given bank statement PDF file and returns its contents as a pandas DataFrame.

        dataframe:
            pd.DataFrame: A DataFrame containing the parsed data from the bank statement PDF file.

            The DataFrame has six columns:
                'date' (datetime), 'valuta' (datetime), 'issuer' (str), 'type' (str)
                'description' (str), and 'amount' (float).
        """
        self.source_file = Path(source_file)
        self._df: Optional[pd.DataFrame] = None
        self.data = BankStatement()
        self._results = dict()

    @property
    def dataframe(self) -> pd.DataFrame:
        if self._df is None:
            data = pd.DataFrame(self.results)
            data["date"] = pd.to_datetime(data["date"], format="%d.%m.%Y")
            data["valuta"] = pd.to_datetime(data["valuta"], format="%d.%m.%Y")
            self._df = data

        return self._df

    @property
    def results(self) -> dict:
        if not self._results:
            self.parse_ing_bank_statement()

        return self._results

    def parse_ing_bank_statement(self):
        self._results = {"date": [], "valuta": [], "issuer": [], "type": [], "description": [], "amount": []}
        self.data.clear_transactions()

        skip_next_line = False
        lines = self._read_pdf()

        for idx, line in enumerate(lines):
            self._parse_statement_fields(line, self.data)
            if skip_next_line:
                skip_next_line = False
                continue

            if self._parse_transaction_line(line):
                # -- Did the previous line contained a valid entry
                #    then read the following line with transaction description
                self._parse_description(lines, idx)
                skip_next_line = True

        # -- Store transactions data
        for idx in range(len(self._results['date'])):
            self.data.add_transaction(
                Transaction(
                    date=to_iso_date(self._results['date'][idx]),
                    valuta=to_iso_date(self._results['valuta'][idx]),
                    issuer=self._results['issuer'][idx],
                    description=self._results['description'][idx],
                    amount=self._results['amount'][idx],
                    type=self._results['type'][idx]
                )
            )

    def _read_pdf(self) -> List[str]:
        lines = list()
        reader = PdfReader(self.source_file)

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
        self._results["date"].append(date_string)
        self._results["amount"].append(amount)
        self._results["issuer"].append(issuer)
        self._results["type"].append(tr_type)

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
            self._results["description"][-1] += "\n" + line.strip()

    def _parse_first_description_line(self, line):
        valuta = self._DATE_REGEX.search(line)
        if valuta is not None:
            valuta = valuta.group(0)
            description = line[len(valuta):].strip()
            self._results["valuta"].append(valuta)
            self._results["description"].append(description)

    def __str__(self):
        return str(self.data)
