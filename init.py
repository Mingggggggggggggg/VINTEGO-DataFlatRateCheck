# Der Aufbau dieser Anwendung geht gegen meine Überzeugung, nur aufgabenspezifische Anwendungen zu schreiben.
# Der "Kunde" wünscht sich jedoch diese Anwendung für mehrere Usecases zu verallgemeinern.
import argparse
import os
import sys
import logger as log
import dataManager as dM

dataPath = f"C:\\VINTEGO-Technik\\Data"
dataFile = "data.json"
fullDataPath = os.path.join(dataPath, dataFile)

globalLog = []

def getArgs():
    parser = argparse.ArgumentParser(
        prog="VINDFR",
        description=(
            "VINTEGO DataFlatRate (VINDFR)"
            "Anwendung zur Ausgabe von Ordnern, die eine gegebene Maximalgröße "
            "überschritten haben. Möglichkeit zum Hinzufügen, Bearbeiten und "
            "Entfernen von Zielpfaden."
        ),
        epilog=(
            "Zielpfaddaten werden in einer JSON gespeichert und abgerufen. "
            "Ergebnisse werden als Logdatei oder in Ninja als Ergebnis ausgegeben."
        ),
        add_help=True
    )

    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-C", "--check",
        action="store_true",
        help="Prüfe Ordnergrößen und gebe Zielpfade mit Überschreitungen aus"
    )
    mode_group.add_argument(
        "-aC", "--addClient",
        action="store_true",
        help="Füge Zielpfad hinzu"
    )
    mode_group.add_argument(
        "-eC", "--editClient",
        action="store_true",
        help="Bearbeite Zielpfad"
    )
    mode_group.add_argument(
        "-dC", "--delClient",
        action="store_true",
        help="Entferne Zielpfad"
    )

    parser.add_argument(
        "-zP", "--zielPfad",
        help="Auswahl des Pfades, welches in der Data.json hinterlegt ist"
    )
    parser.add_argument(
        "-S", "--setSize",
        help="Setze Größe in GB für Zielpfad (nur bei add/edit erlaubt)"
    )
    parser.add_argument(
        "-wS", "--warnSizePercent",
        type=int,
        help="Prozent von maxSize, ab der eine Meldung ausgegeben werden soll. Erfordert check"
    )
    parser.add_argument(
        "-nST", "--noSkipToday",
        action="store_false",
        help="Überspringe Checks für Ordner, die heute bereits durchlaufen wurden. Bei Angabe werden die Checks nicht übersrpungen."
    )
    return parser.parse_args()


def main():
    args = getArgs()
    log.cleanLog()

    globalLog.append("Überprüfe Eingabekombinationen auf Korrektheit")
    # Kombinationsprüfungen
    if args.delClient and args.setSize:
        globalLog.append("Fehler: --setSize darf nicht mit --delClient verwendet werden.")
        log.logMessageHeader("Global Log", globalLog, top=True)
        sys.exit("Fehler: --setSize darf nicht mit --delClient verwendet werden.")

    if args.check:
        # --check darf nicht mit Pfad- oder Size-Parametern kombiniert werden
        if args.zielPfad or args.setSize:
            globalLog.append("Fehler: --check darf nicht mit --zielPfad oder --setSize kombiniert werden.")
            log.logMessageHeader("Global Log", globalLog, top=True)
            sys.exit("Fehler: --check darf nicht mit --zielPfad oder --setSize kombiniert werden.")
        # --warnSizePercent wird zwingend benötigt
        if not args.warnSizePercent:
            globalLog.append("Fehler: --check erfordert die Angabe von --warnSizePercent.")
            log.logMessageHeader("Global Log", globalLog, top=True)
            sys.exit("Fehler: --check erfordert --warnSizePercent.")

    # Prüfen, dass mindestens ein Modus gewählt wurde
    if not (args.check or args.addClient or args.editClient or args.delClient):
        globalLog.append("Fehler: Kein Modus ausgewählt. Bitte --check, --addClient, --editClient oder --delClient verwenden.")
        log.logMessageHeader("Global Log", globalLog, top=True)
        sys.exit("Fehler: Kein Modus ausgewählt.")



    globalLog.append("Keine Kombinationskonflikte gefunden. Starte Integritätsprüfung")

    print("Starte Data Integritätsprüfung")
    if not (dM.checkDataIntegrity(fullDataPath)):
        globalLog.append("Data Integritätsprüfung fehlgeschlagen. Bitte Logeintrag überprüfen")
        log.logMessageHeader("Global Log", globalLog, top=True)
        sys.exit("Data Integritätsprüfung fehlgeschlagen. Bitte Logeintrag überprüfen")

    if args.check:
        globalLog.append(f"Prüfen ausgewählt. Starte Prüfungen. Größenwarnungen bei Überschreitung von {args.warnSizePercent}% werden im Log ausgegeben")
        try:
            dM.runCheck(fullDataPath, args.warnSizePercent, args.noSkipToday)
        except Exception as e:
            print(e)
        return f"Modus: Prüfen | warnSizePercent={args.warnSizePercent}"
    elif args.addClient:
        globalLog.append(f"Hinzufügen ausgewählt. Pfad: {args.zielPfad} mit Größe: {args.setSize} werden hinzugefügt")
        dM.addData(fullDataPath, args.zielPfad, args.setSize)
        return f"Modus: Zielpfad hinzufügen | Name={args.zielPfad} | Size={args.setSize}"
    elif args.editClient:
        globalLog.append(f"Bearbeitung ausgewählt. {args.zielPfad} wird mit MaxSize: {args.setSize} der Liste hinzugefügt")
        dM.editData(fullDataPath, args.zielPfad, args.setSize)
        return f"Modus: Zielpfad bearbeiten | Name={args.zielPfad} | Size={args.setSize}"
    elif args.delClient:
        globalLog.append(f"Löschen ausgewählt. {args.zielPfad} und die dazu korrespondierende Einträge werden entfernt")
        dM.delData(fullDataPath, args.zielPfad)
        return f"Modus: Zielpfad löschen | Name={args.zielPfad}"

    log.logMessageHeader("GlobalLog", globalLog, top=True)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Anwendung durch Nutzer beendet")


#python -m PyInstaller --onefile init.py -n VINDFR