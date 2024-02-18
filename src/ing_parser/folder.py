from pathlib import Path
from typing import Union, Optional

import pandas as pd

from ing_parser.base import IngBase
from ing_parser.statement import IngStatement


class IngStatementsFolder(IngBase):
    def __init__(self, source_directory: Union[str, Path], account_type: str = 'Giro'):
        self.source_directory = Path(source_directory)
        self.account_type = account_type
        self._df: Optional[pd.DataFrame] = None

    @property
    def dataframe(self) -> pd.DataFrame:
        if self._df is None:
            self._df = self.parse()
        return self._df

    def parse(self):
        dataframes = list()

        for file in self.source_directory.glob("*.pdf"):
            if self.SEARCH_TERM in file.name.lower() and self.account_type in file.name.lower():
                ing_statement = IngStatement(file)
                dataframes.append(ing_statement.dataframe)

        return pd.concat(dataframes)
