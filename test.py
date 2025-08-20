import time
import locale

print(locale.setlocale(locale.LC_TIME, "German_Germany.1252"))

print(time.strftime("%d.%m.%Y"))