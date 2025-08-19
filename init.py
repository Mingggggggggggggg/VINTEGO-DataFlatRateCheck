import argparse
import sys
import logger
import dataManager

def getArgs():
    parser = argparse.ArgumentParser(prog="VOGC",
                                     description="VINTEGO OrdnerGrößenCheck (VOGC)" \
                                     "Anwendung zur Ausgabe von Ordnern, die eine gegebene Mindestgröße überschritten haben. " \
                                     "Möglichkeit zum Hinzufügen, Bearbeiten und Entfernen von Kunden",
                                     epilog="Kundendaten werden in einer JSON gespeichert und abgerufen. " \
                                     "Ergebnisse werden als Logdatei oder in Ninja als Ergebnis ausgegeben.",
                                     add_help=False)
    parser.add_argument("selectServer", 
                        help="Servername -> Unterschiedliche Ordnerpfade")
    parser.add_argument("-mS", "--minSize", 
                        help="Mindestgröße zur Meldung von Kundenordnern")
    
    mode_group = parser.add_mutually_exclusive_group()

    mode_group.add_argument("-aC", "--addClient",
                        action="store_true",
                        help="Füge Kunden hinzu")
    mode_group.add_argument("-eC", "--editClient",
                        action="store_true", 
                        help="Bearbeite Kunden")
    mode_group.add_argument("-dC", "--delClient",
                        action="store_true", 
                        help="Entferne Kunden")
    parser.add_argument("-kN", "--kundenNamen", 
                        help="Kundennamen")
    parser.add_argument("-S", "--setSize", 
                        help="Setze Größe für Kunden")
    return parser.parse_args()


def main():
    args = getArgs()

    # Validiere Kombinationen
    if args.delClient & args.setSize:
        sys.exit("Fehler: --setSize ist nicht mit --delClient erlaubt.")

    if not (args.addClient | args.editClient | args.delClient):
        sys.exit("Fehler: Kein Modus ausgewählt. Nutze --addClient, --editClient oder --delClient.")

    if args.addClient:

        return f"Modus: Kunde hinzufügen | Name={args.kundenNamen} | Size={args.setSize}"
    elif args.editClient:
        return f"Modus: Kunde bearbeiten | Name={args.kundenNamen} | Size={args.setSize}"
    elif args.delClient:
        return f"Modus: Kunde löschen | Name={args.kundenNamen}"
