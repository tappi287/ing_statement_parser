# ING Kontoauszug Parser
based on [kaiklede/ing-kontoauszug-parser](https://github.com/kaiklede/ing-kontoauszug-parser).

This version uses refactored code and extends the parser with new columns:

`"date";"valuta";"issuer";"type";"description";"amount"`

This should make it more usable to import data into a tool like [Hibiscus](https://www.willuhn.de/products/hibiscus/)

## Setup
1. Install [Python 3.11](https://python.org) and [poetry](https://python-poetry.org/docs/#installation)
2. Clone or download the repository `git clone https://github.com/tappi287/ing_statement_parser.git`
3. install the dependencies: `poetry install`

## Usage
For example, if you want to parse `kontoauszug.pdf`:
```
poetry run ingparser kontoauszug.pdf
```

You can use ```poetry run ingparser --help``` to see further options

```
usage: ingparser.py [-h] [-a ACCOUNT] [-o OUTPUT] INPUT

positional arguments:
  INPUT                 Can be a file or a directory with the ING PDF files

options:
  -h, --help            show this help message and exit
  -a ACCOUNT, --account ACCOUNT
                        Account type to parse if directory is specified e.g. Giro, Extra (Default: Giro)
  -o OUTPUT, --output OUTPUT
                        Output file (Default: ing_kontoauszug.csv)
```
