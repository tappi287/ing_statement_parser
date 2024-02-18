import re


class IngBase:
    # Not in use
    TYPES = (
    "lastschrift", "ueberweisung", "entgelt", "dauerauftrag/terminueberw.", "gehalt/rente", "gutschrift", "abbuchung",
    "retoure")

    SEARCH_TERM = "kontoauszug"
    DATE_REGEX = re.compile(r"^(0[1-9]|[12]\d|3[01])[.](0[1-9]|1[012])[.](19|20)\d{2}")
    AMOUNT_REGEX = re.compile(r"(-?(\d{1,3}(\.\d{3})*|\d+),\d{2})$")
