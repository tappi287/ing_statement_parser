import logging
from pathlib import Path
from typing import Union, Optional, List
import concurrent.futures

import pandas as pd

from ing_parser.base import IngBase
from ing_parser.statement import IngStatement


class IngStatementsFolder(IngBase):
    def __init__(self, source_directory: Union[str, Path], account_type: str = 'Giro'):
        self.source_directory = Path(source_directory)
        self.account_type = account_type.lower()
        self._df: Optional[pd.DataFrame] = None
        self.statements: List[IngStatement] = list()

    @property
    def dataframe(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self.parse()
        return self._df

    @staticmethod
    def process_file(file_path: Path):
        ing_statement = IngStatement(file_path)
        ing_statement.parse_ing_bank_statement()
        return ing_statement

    def parse(self):
        pdf_files = list()
        for file in self.source_directory.glob("*.pdf"):
            if self._SEARCH_TERM in file.name.lower() and self.account_type in file.name.lower():
                pdf_files.append(file)

        # Use ThreadPoolExecutor to process the files concurrently
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.process_file, file) for file in pdf_files]

            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                ing_statement = future.result()
                self.statements.append(ing_statement)
                logging.info(f"Completed parsing {len(self.statements)}/{len(pdf_files)} files")

        return pd.concat([s.dataframe for s in self.statements])
