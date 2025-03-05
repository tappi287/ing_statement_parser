from pathlib import Path

from ing_parser.folder import IngStatementsFolder
from ing_parser.statement import IngStatement
from ing_parser.io import yaffa, ez

def test_parser():
    test_file = Path(r'I:\Nextcloud\Documents\Konto\ING-Giro\Girokonto_5422021297_Kontoauszug_20171101.pdf')
    statement = IngStatement(test_file)
    print(statement.dataframe)
    assert len(statement.data.transactions) > 0


def print_unique_types(df):
    unique_types = df['type'].unique()
    for _type in unique_types:
        print(_type)


def test_folder():
    test_path = Path(r'I:\Nextcloud\Documents\Konto\ING-Giro')
    f = IngStatementsFolder(test_path)

    df = f.dataframe
    df = df.sort_values("date", ascending=False)
    df.to_csv(Path(__file__).parent / "TestExport.csv", index=False, sep=";", quoting=1)
    print_unique_types(df)
    print("Fin")


def test_ez_export():
    test_file = Path(r'I:\Nextcloud\Documents\Konto\ING-Giro\Girokonto_5422021297_Kontoauszug_20171101.pdf')
    statement = IngStatement(test_file)
    ez_transactions = ez.EzBookKeepingTransactions.from_bank_statement(statement.data)
    assert len(ez_transactions) == len(statement.data.transactions)


def test_ez_folder_convert():
    test_path = Path(r'I:\Nextcloud\Documents\Konto\ING-Giro')
    f = IngStatementsFolder(test_path)
    f.parse()
    ez_df = ez.convert_to_ez_dataframe([f.data for f in f.statements])

    ez_df = ez_df.sort_values("Time", ascending=False)
    ez.export_ez_csv(Path(__file__).parent / "TestExport_EZ.csv", ez_df)


def test_yaffa_convert():
    test_file = Path(r'I:\Nextcloud\Documents\Konto\ING-Giro\Girokonto_5422021297_Kontoauszug_20171101.pdf')
    statement = IngStatement(test_file)
    yaffa_statement = yaffa.convert_statement_to_yaffa(statement.data)

    print(yaffa_statement.dataframe)

    df = yaffa_statement.dataframe
    df = df.sort_values("date", ascending=False)
    df.to_csv(Path(__file__).parent / "TestExport.csv", index=False, sep=";", quoting=1)

    assert len(yaffa_statement.transactions) > 0


def test_folder_yaffa():
    test_path = Path(r'I:\Nextcloud\Documents\Konto\ING-Giro')
    f = IngStatementsFolder(test_path)

    df = f.dataframe
    df = df.sort_values("date", ascending=False)
    df.to_csv(Path(__file__).parent / "TestExport.csv", index=False, sep=";", quoting=1)
    print("Fin")