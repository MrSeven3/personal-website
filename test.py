import datetime
import dateparser

test = dateparser.parse("2026-05-17 15:42:38") - dateparser.parse("2026-05-17 15:41:38")
