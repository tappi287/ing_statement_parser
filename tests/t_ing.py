from pathlib import Path

from ing_parser.folder import IngStatementsFolder
from ing_parser.statement import IngStatement


def test_parser():
    test_file = Path(r'I:\Nextcloud\Documents\Konto\ING-Giro\Girokonto_5422021297_Kontoauszug_20171101.pdf')
    statement = IngStatement(test_file)
    print(statement.dataframe)
    assert len(statement.data.transactions) > 0


def test_folder():
    test_path = Path(r'I:\Nextcloud\Documents\Konto\ING-Giro')
    f = IngStatementsFolder(test_path)

    df = f.dataframe
    df = df.sort_values("date", ascending=False)
    print("Fin")