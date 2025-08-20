import json
import locale
import os
import time
import logger as log

def getDirSize(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)

    size_in_gb = total_size / (1024 ** 3)
    return round(size_in_gb, 3)  

def createData(fullDataPath):
    os.makedirs(os.path.dirname(fullDataPath), exist_ok=True)
    with open(fullDataPath, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2, ensure_ascii=False)
    log.logMessage(f"JSON wurde in {fullDataPath} erstellt. Bitte befüllen.")
    print(f"{fullDataPath} wurde neu erstellt. Bitte befüllen.")

def loadData(fullDataPath):
    with open(fullDataPath, "r", encoding="utf-8") as f:
            data = json.load(f)
    return data

def saveData(fullDataPath, data):
    try:
        with open(fullDataPath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log.logMessage("Speichervorgang erfolgreich")
        print("Speichervorgang erfolgreich")   
    except Exception as e:
        log.logMessage("Fehler: Speichervorgang fehlgeschlagen")
        print("Fehler: Speichervorgang fehlgeschlagen")
        

def addData(fullDataPath, name, maxSize):
    data = loadData(fullDataPath)

    for i in data:
        if (i["Pfad"] == name):
            msg = f"Der Pfad {name} existiert bereits in der JSON"
            print(msg)
            log.logMessage(msg)
    
    addClient = {
        "Pfad": name,
        "MaxSize": maxSize,
        "LastCheck": None,
        "LastSize": None
    }

    data.append(addClient)
    msg = f"Starte Speichervorgang für {name} mit MaxSize {maxSize}"

    print(msg)
    log.logMessage(msg)
    saveData(fullDataPath, data)


def editData(fullDataPath, name, newMaxSize):
    data = loadData(fullDataPath)

    isEntry = False

    for i in data:
        if i["Pfad"] == name:
            i["MaxSize"] = newMaxSize
            isEntry = True
            break
    if not isEntry:
        print(f"Fehler: Pfad {name} existiert nicht oder wurde nicht gefunden")
        return False

    msg = f"Starte Speichervorgang für {name} mit neuer MaxSize {newMaxSize}"
    print(msg)
    log.logMessage(msg)
    saveData(fullDataPath, data)

def delData(fullDataPath, name):
    data = loadData(fullDataPath)

    for i in data:
        if i["Pfad"] == name:
            #i.pop(name, None)
            data.remove(i)
            break
    
    msg = f"Starte Speichervorgang der neuen Liste aus der {name} und die korrespondierenden Einträge entfernt wurden"
    print(msg)
    log.logMessage(msg)
    saveData(fullDataPath, data)


def checkDataIntegrity(fullDataPath):
    if os.path.exists(fullDataPath):
        try:
            data = loadData(fullDataPath)

            seen = set()
            changed = False
            for k in data:
                
                if not all(field in k for field in ("Pfad", "MaxSize")):
                    print(f"Fehler: Für Eintrag {k} fehlen Felder oder wurden falsch geschrieben.")
                    return False

                # Prüfe auf Duplikate (Sehr teuer)
                if k["Pfad"] in seen:
                    print(f"Fehler: Duplikat bei Pfad {k["Pfad"]}")
                    return False
                seen.add(k["Pfad"])
                
                #Ergänze optionale Ergebnisfelder LastCheck und LastSize
                if "LastCheck" not in k:
                    k["LastCheck"] = None
                    changed = True
                if "LastSize" not in k:
                    k["LastSize"] = None
                    changed = True

            if changed:
                with open(fullDataPath, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("Integritätscheck: Fehlende optionale Ergebnisfelder LastCheck (logisches)oder LastSize ergänzt.")
            return True
        except Exception as e:
            print(f"Fehler beim Laden von {fullDataPath}: {e}")
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
            continue

        print(f"Größe für {i['Pfad']} wird berechnet")
        newSize = getDirSize(i["Pfad"])

        # Aktualisiere Eintrag
        i["LastCheck"] = currentDate
        i["LastSize"] = newSize

        print(f"{i['Pfad']} mit Größe {newSize}")


    for j in data:
        if j["LastCheck"] != currentDate:
            continue
        if j["LastSize"] >= j["MaxSize"] * (warnSizePercent / 100):
            msg = (f"Der Ordner '{j['Pfad']}' liegt im Warnbereich mit einer Größe von {j['LastSize']} "
                f"\nDie Warngrenze von {j['MaxSize'] * (warnSizePercent / 100)} wurde überschritten.")
            print(msg)
            marked.append(msg)
    
    saveData(fullDataPath, data)
    log.logMessageHeader("Warnung", marked)
    
'''
if __name__ == "__main__":
    #checkDataIntegrity(f"C:\\VINTEGO-Technik\\Data\\data.json")
    #delData(f"C:\\VINTEGO-Technik\\Data\\data.json", f"C:\\Temp\\Test")
    #addData("C:\\VINTEGO-Technik\\Data\\data.json", "Superpenis", 10)
    #editData("C:\\VINTEGO-Technik\\Data\\data.json", "Superpenis", 5)
'''