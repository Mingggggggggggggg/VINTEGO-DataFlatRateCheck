# Der Aufbau dieser Anwendung geht gegen meine Überzeugung, nur aufgabenspezifische Anwendungen zu schreiben.
# Der "Kunde" wünscht sich jedoch diese Anwendung für mehrere Usecases zu verallgemeinern.
import argparse
import sys
import logger
import dataManager as dM

dataPath = f"C:\\VINTEGO-Technik\\Data"
dataFile = "data.json"

def getArgs():
    parser = argparse.ArgumentParser(
        prog="VOGC",
        description=(
            "VINTEGO OrdnerGrößenCheck (VOGC) "
            "Anwendung zur Ausgabe von Ordnern, die eine gegebene Maximalgröße "
            "überschritten haben. Möglichkeit zum Hinzufügen, Bearbeiten und "
            "Entfernen von Kunden."
        ),
        epilog=(
            "Kundendaten werden in einer JSON gespeichert und abgerufen. "
            "Ergebnisse werden als Logdatei oder in Ninja als Ergebnis ausgegeben."
        ),
        add_help=True
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-C", "--check",
        action="store_true",
        help="Prüfe Ordnergrößen und gebe Kunden mit Überschreitungen aus"
    )
    mode_group.add_argument(
        "-aC", "--addClient",
        action="store_true",
        help="Füge Kunden hinzu"
    )
    mode_group.add_argument(
        "-eC", "--editClient",
        action="store_true",
        help="Bearbeite Kunden"
    )
    mode_group.add_argument(
        "-dC", "--delClient",
        action="store_true",
        help="Entferne Kunden"
    )

    parser.add_argument(
        "-kN", "--kundenNamen",
        help="Kundennamen"
    )
    parser.add_argument(
        "-S", "--setSize",
        help="Setze Größe für Kunden (nur bei add/edit erlaubt)"
    )
    parser.add_argument(
        "-sP", "--sizePercentage",
        type=int,
        help="Prozent von maxSize, ab der eine Meldung ausgegeben werden soll"
    )
    parser.add_argument(
        "-sT", "--skipToday",
        action="store_true",
        help="Überspringe Checks für Ordner, die heute bereits durchlaufen wurden. Bei Angabe werden die Checks nicht übersrpungen."
    )
    return parser.parse_args()


def main():
    args = getArgs()


    if args.delClient and args.setSize:
        sys.exit("Fehler: --setSize ist nicht mit --delClient erlaubt.")
    if args.check and (args.kundenNamen or args.setSize):
        sys.exit("Fehler: --check darf nicht mit Kundendaten kombiniert werden.")
    if not (args.check or args.addClient or args.editClient or args.delClient):
        sys.exit("Fehler: Kein Modus ausgewählt. Nutze --check, --addClient, --editClient oder --delClient.")

    dM.checkDataIntegrity(dataPath, dataFile)

    if args.check:
        dM.runCheck()
        return f"Modus: Prüfen | sizePercentage={args.sizePercentage}"
    elif args.addClient:
        dM.addData(args.kundenNamen, args.setSize)
        return f"Modus: Kunde hinzufügen | Name={args.kundenNamen} | Size={args.setSize}"
    elif args.editClient:
        dM.editData(args.kundenNamen, args.setSize)
        return f"Modus: Kunde bearbeiten | Name={args.kundenNamen} | Size={args.setSize}"
    elif args.delClient:
        dM.delData(args.kundenNamen)
        return f"Modus: Kunde löschen | Name={args.kundenNamen}"

