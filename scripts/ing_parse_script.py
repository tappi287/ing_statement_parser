import argparse
from pathlib import Path
from sys import stderr

from ing_parser.folder import IngStatementsFolder
from ing_parser.statement import IngStatement


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "path",
        metavar="INPUT",
        type=str,
        help="Can be a file or a directory with the ING PDF files",
    )
    # -a, --account
    parser.add_argument(
        "-a",
        "--account",
        type=str,
        required=False,
        default="giro",
        help="Account type to parse if directory is specified e.g. Giro, Extra (Default: Giro)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        required=False,
        default="ing_kontoauszug.csv",
        help="Output file (Default: ing_kontoauszug.csv)",
    )
    args = parser.parse_args()

    path = Path(args.path)

    if path.is_file() and path.suffix.casefold() == ".pdf":
        df = IngStatement(path).dataframe
    elif path.is_dir():
        df = IngStatementsFolder(path, args.account.lower()).dataframe
    else:
        print(f"Invalid input: {path}", file=stderr)
        exit(1)

    df = df.sort_values("date", ascending=False)
    df.to_csv(args.output, index=False, sep=";", quoting=1)


if __name__ == "__main__":
    main()
