# Der Aufbau dieser Anwendung geht gegen meine ueberzeugung, nur aufgabenspezifische Anwendungen zu schreiben.
# Der "Kunde" wuenscht sich jedoch diese Anwendung fuer mehrere Usecases zu verallgemeinern.
import argparse
import os
import sys
import loggerResult as logR
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
            "Anwendung zur Ausgabe von Ordnern, die eine gegebene Maximalgroesse "
            "ueberschritten haben. Moeglichkeit zum Hinzufuegen, Bearbeiten und "
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
        help="Pruefe Ordnergroessen und gebe Zielpfade mit ueberschreitungen aus. " \
        "(Erfordert warnSizePercent. Optional noSkipToday)"
    )
    mode_group.add_argument(
        "-aC", "--addClient",
        action="store_true",
        help="Fuege Zielpfad und maximale Groesse in GB hinzu. " \
        "(Erfordert Zielpfad und setSize)"
    )
    mode_group.add_argument(
        "-eC", "--editClient",
        action="store_true",
        help="Bearbeite Zielpfad um eine neue maximalgroesse in GB" \
        "(Erfordert Zielpfad und setSize)"

    )
    mode_group.add_argument(
        "-dC", "--delClient",
        action="store_true",
        help="Entferne Zielpfad und koresspondierende Eintraege" \
        "(Erfordert Zielpfad)"
    )

    parser.add_argument(
        "-zP", "--zielPfad",
        help="Auswahl oder Nennung des Pfades, welches in der Data.json hinterlegt ist/wird. " \
        "(Nur bei Hinzufuegen, Bearbeiten und Entfernen)"
    )
    parser.add_argument(
        "-S", "--setSize",
        help="Setze Groesse in GB fuer Zielpfad " \
        "(Nur bei Hinzufuegen und Bearbeiten)"
    )
    parser.add_argument(
        "-wS", "--warnSizePercent",
        type=float,
        help="Prozent von maxSize, ab der eine Meldung ausgegeben werden soll. " \
        "(Erfordert check)"
    )
    parser.add_argument(
        "-nST", "--noSkipToday",
        action="store_false",
        help="ueberspringe Checks fuer Ordner, die heute bereits durchlaufen wurden. Bei Angabe werden die Checks nicht uebersrpungen." \
        "(Optional bei Check)"
    )
    return parser.parse_args()


def main():
    args = getArgs()
    logR.cleanLog()

    globalLog.append("Ueberpruefe Eingabekombinationen auf Korrektheit")
    # Kombinationspruefungen
    if args.delClient and args.setSize:
        globalLog.append("Fehler: --setSize darf nicht mit --delClient verwendet werden.")
        logR.logMessageHeader("Global Log", globalLog, top=True)
        sys.exit("Fehler: --setSize darf nicht mit --delClient verwendet werden.")

    if args.check:
        # --check darf nicht mit Pfad- oder Size-Parametern kombiniert werden
        if args.zielPfad or args.setSize:
            globalLog.append("Fehler: --check darf nicht mit --zielPfad oder --setSize kombiniert werden.")
            logR.logMessageHeader("Global Log", globalLog, top=True)
            sys.exit("Fehler: --check darf nicht mit --zielPfad oder --setSize kombiniert werden.")
        # --warnSizePercent ist erforderlich
        if not args.warnSizePercent:
            globalLog.append("Fehler: --check erfordert die Angabe von --warnSizePercent.")
            logR.logMessageHeader("Global Log", globalLog, top=True)
            sys.exit("Fehler: --check erfordert --warnSizePercent.")

    # Pruefe, dass mindestens ein Modus gewaehlt wurde
    if not (args.check or args.addClient or args.editClient or args.delClient):
        globalLog.append("Fehler: Kein Modus ausgewaehlt. Bitte --check, --addClient, --editClient oder --delClient verwenden.")
        logR.logMessageHeader("Global Log", globalLog, top=True)
        sys.exit("Fehler: Kein Modus ausgewaehlt.")



    globalLog.append("Keine Kombinationskonflikte gefunden. Starte Integritaetspruefung")

    print("Starte Data Integritaetspruefung")
    if not (dM.checkDataIntegrity(fullDataPath)):
        globalLog.append("Data Integritaetspruefung fehlgeschlagen. Bitte Logeintrag ueberpruefen")
        print("Data Integritaetspruefung fehlgeschlagen. Bitte Logeintrag ueberpruefen")
        logR.logMessageHeader("Global Log", globalLog, top=True)
        #sys.exit("Data Integritaetspruefung fehlgeschlagen. Bitte Logeintrag ueberpruefen")

    if args.check:
        globalLog.append(f"Pruefen ausgewaehlt. Starte Pruefungen. Groessenwarnungen bei Ueberschreitung von {args.warnSizePercent}% werden im Log ausgegeben")
        try:
            dM.runCheck(fullDataPath, args.warnSizePercent, args.noSkipToday)
        except Exception as e:
            print(e)
        logR.logMessageHeader("GlobalLog", globalLog, top=True)
        return f"Modus: Pruefen | warnSizePercent={args.warnSizePercent}"
    elif args.addClient:
        globalLog.append(f"Hinzufuegen ausgewaehlt. Pfad: {args.zielPfad} mit Groesse: {args.setSize} werden hinzugefuegt")
        dM.addData(fullDataPath, args.zielPfad, args.setSize)
        logR.logMessageHeader("GlobalLog", globalLog, top=True)
        return f"Modus: Zielpfad hinzufuegen | Name={args.zielPfad} | Size={args.setSize}"
    elif args.editClient:
        globalLog.append(f"Bearbeitung ausgewaehlt. {args.zielPfad} wird mit MaxSize: {args.setSize} der Liste hinzugefuegt")
        dM.editData(fullDataPath, args.zielPfad, args.setSize)
        logR.logMessageHeader("GlobalLog", globalLog, top=True)
        return f"Modus: Zielpfad bearbeiten | Name={args.zielPfad} | Size={args.setSize}"
    elif args.delClient:
        globalLog.append(f"Loeschen ausgewaehlt. {args.zielPfad} und die dazu korrespondierende Eintraege werden entfernt")
        dM.delData(fullDataPath, args.zielPfad)
        logR.logMessageHeader("GlobalLog", globalLog, top=True)
        return f"Modus: Zielpfad loeschen | Name={args.zielPfad}"



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Anwendung durch Nutzer beendet")


#python -m PyInstaller --onefile init.py -n VINDFR