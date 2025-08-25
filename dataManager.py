import json
import locale
import os
import time
import loggerChanges as logC
import loggerResult as logR

def getDirSize(path):
    if not os.path.exists(path):
        msg = f"Der Pfad {path} existiert nicht."
        print(msg)
        logC.logMessage(msg)
        return 0

    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                if os.path.isfile(fp):
                    total_size += os.path.getsize(fp)
            except (FileNotFoundError, PermissionError) as e:
                msg = f"{fp} konnte nicht gelesen werden: {e}"
                print(msg)
                logC.logMessage(msg)

    size_in_gb = total_size / (1024 ** 3)
    return round(size_in_gb, 3)


def createData(fullDataPath):
    os.makedirs(os.path.dirname(fullDataPath), exist_ok=True)
    with open(fullDataPath, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2, ensure_ascii=False)
    logC.logMessage(f"JSON wurde in {fullDataPath} erstellt. Bitte befuellen.")
    print(f"{fullDataPath} wurde neu erstellt. Bitte befuellen.")

def loadData(fullDataPath):
    with open(fullDataPath, "r", encoding="utf-8") as f:
            data = json.load(f)
    return data

def saveData(fullDataPath, data):
    try:
        with open(fullDataPath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logC.logMessage("Speichervorgang erfolgreich")
        print("Speichervorgang erfolgreich")   
    except Exception as e:
        logC.logMessage("Fehler: Speichervorgang fehlgeschlagen")
        print("Fehler: Speichervorgang fehlgeschlagen")
        

def addData(fullDataPath, name, maxSize):
    try:
        data = loadData(fullDataPath)
    except FileNotFoundError:
        name = clearInput(name)
        addClient = {
            'Pfad': name,
            "MaxSize": float(maxSize),
            "LastCheck": None,
            "LastSize": None
        }
        saveData(fullDataPath, [addClient])
        print(f"JSON neu erstellt und {name} mit MaxSize {maxSize} hinzugefuegt")
        logC.logMessage(f"JSON neu erstellt und {name} mit MaxSize {maxSize} hinzugefuegt")
        return

    name = clearInput(name)

    for i in data:
        if i['Pfad'] == name:
            print(f"Der Pfad {name} existiert bereits in der JSON")
            logC.logMessage(f"Der Pfad {name} existiert bereits in der JSON")
            return
    
    addClient = {
        'Pfad': name,
        "MaxSize": float(maxSize),
        "LastCheck": None,
        "LastSize": None
    }

    data.append(addClient)

    print(f"Starte Speichervorgang fuer {name} mit MaxSize {maxSize}")
    logC.logMessage(f"Starte Speichervorgang fuer {name} mit MaxSize {maxSize}")
    saveData(fullDataPath, data)

def clearInput(name):
    if not name:
        return ""

        # Normale Pfad-Schreibweise (z.B. \\ statt /, je nach OS)
    normalized = os.path.normpath(name)

    # JSON-sicher: Backslashes doppeln
    safe_path = normalized.replace("\\", "\\\\")

    return safe_path


def editData(fullDataPath, name, newMaxSize):
    data = loadData(fullDataPath)

    isEntry = False

    for i in data:
        if i['Pfad'] == name:
            i["MaxSize"] = float(newMaxSize)
            isEntry = True
            break
    if not isEntry:
        print(f"Fehler: Pfad {name} existiert nicht oder wurde nicht gefunden")
        logC.logMessage(f"Fehler: Pfad {name} existiert nicht oder wurde nicht gefunden")
        return False

    print(f"Starte Speichervorgang fuer {name} mit neuer MaxSize {newMaxSize}")
    logC.logMessage(f"Starte Speichervorgang fuer {name} mit neuer MaxSize {newMaxSize}")
    saveData(fullDataPath, data)

def delData(fullDataPath, name):
    data = loadData(fullDataPath)

    for i in data:
        if i['Pfad'] == name:
            #i.pop(name, None)
            data.remove(i)
            break
    
    print(f"Starte Speichervorgang der neuen Liste aus der {name} und die korrespondierenden Eintraege entfernt wurden")
    logC.logMessage(f"Starte Speichervorgang der neuen Liste aus der {name} und die korrespondierenden Eintraege entfernt wurden")
    saveData(fullDataPath, data)


def checkDataIntegrity(fullDataPath):
    if os.path.exists(fullDataPath):
        try:
            data = loadData(fullDataPath)

            seen = set()
            changed = False
            for k in data:
                
                if not all(field in k for field in ("Pfad", "MaxSize")):
                    print(f"Fehler: Fuer Eintrag {k} fehlen Felder oder wurden falsch geschrieben.")
                    logR.logMessage(f"Fehler: Fuer Eintrag {k} fehlen Felder oder wurden falsch geschrieben.")
                    return False

                # Pruefe auf Duplikate (Sehr teuer)
                if k['Pfad'] in seen:
                    print(f"Fehler: Duplikat bei Pfad {k['Pfad']}")
                    logR.logMessage(f"Fehler: Duplikat bei Pfad {k['Pfad']}")
                    return False
                seen.add(k['Pfad'])
                
                #Ergaenze optionale Ergebnisfelder LastCheck und LastSize
                if "LastCheck" not in k:
                    k["LastCheck"] = None
                    changed = True
                if "LastSize" not in k:
                    k["LastSize"] = None
                    changed = True

            if changed:
                with open(fullDataPath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("Integritaetscheck: Fehlende optionale Ergebnisfelder LastCheck (logisches) oder LastSize ergaenzt.")
                logR.logMessage("Integritaetscheck: Fehlende optionale Ergebnisfelder LastCheck (logisches) oder LastSize ergaenzt.")
            return True
        except Exception as e:
            print(f"Fehler beim Laden von {fullDataPath}: {e}")
            logR.logMessage(f"Fehler beim Laden von {fullDataPath}: {e}")
            return False
    else:
        createData(fullDataPath)
        return False

def runCheck(fullDataPath, warnSizePercent, skipToday):
    data = loadData(fullDataPath)

    locale.setlocale(locale.LC_TIME, "German_Germany.1252")
    currentDate = time.strftime("%d.%m.%Y")

    marked = []

    for i in data:
        if ((i["LastCheck"] == currentDate) and skipToday):
            print(f"Eintrag {i['Pfad']} wird uebersprungen, weil er heute bereits geprüft wurde")
            logR.logMessage(f"Eintrag {i['Pfad']} wird uebersprungen, weil er heute bereits geprüft wurde")
            continue

        print(f"Groesse fuer {i['Pfad']} wird berechnet")
        logR.logMessage(f"Groesse fuer {i['Pfad']} wird berechnet")
        newSize = getDirSize(i['Pfad'])

        # Aktualisiere Eintrag
        i["LastCheck"] = currentDate
        i["LastSize"] = newSize

        print(f"{i['Pfad']} mit Groesse {newSize}")
        logR.logMessage(f"{i['Pfad']} mit Groesse {newSize}")


    for j in data:
        if j["LastCheck"] != currentDate:
            continue
        if j["LastSize"] >= j["MaxSize"] * (warnSizePercent / 100):
            print((f"Der Ordner '{j['Pfad']}' liegt im Warnbereich mit einer Groesse von {j['LastSize']} "
                f"\nDie Warngrenze von {j['MaxSize'] * (warnSizePercent / 100)} wurde ueberschritten."))
            marked.append((f"Der Ordner '{j['Pfad']}' liegt im Warnbereich mit einer Groesse von {j['LastSize']} "
                f"\nDie Warngrenze von {j['MaxSize'] * (warnSizePercent / 100)} wurde ueberschritten."))
    
    saveData(fullDataPath, data)
    logR.logMessageHeader("Warnung", marked, top=True)

'''
if __name__ == "__main__":
    #checkDataIntegrity(f"C:\\VINTEGO-Technik\\Data\\data.json")
    #delData(f"C:\\VINTEGO-Technik\\Data\\data.json", f"C:\\Temp\\Test")
    #addData("C:\\VINTEGO-Technik\\Data\\data.json", "Superpenis", 10)
    #editData("C:\\VINTEGO-Technik\\Data\\data.json", "Superpenis", 5)
'''