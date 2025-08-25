import os
from datetime import datetime
fullPath=r"C:\VINTEGO-Technik\Logs\VINDFR_Resultlog.txt"
def cleanLog():
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
    
    with open(fullPath, "w", encoding="utf-8") as file:
        file.write("")

def logMessageHeader(name, data, top=False):
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)

    puffer = len(name)
    dashes = (50 - puffer) // 2

    header = "-" * dashes + f" {name} " + "-" * dashes + "\n"
    footer = "-" * (dashes - 3) + f" End{name} " + "-" * (dashes - 3) + "\n"

    dataBlock = header
    for entry in data:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]
        dataBlock += f"{timestamp} - {entry}\n"
    dataBlock += footer

    if top:
        if os.path.exists(fullPath):
            with open(fullPath, "r", encoding="utf-8") as file:
                existing_content = file.read()
        else:
            existing_content = ""

        with open(fullPath, "w", encoding="utf-8") as file:
            file.write(dataBlock + existing_content)
    else:
        with open(fullPath, "a", encoding="utf-8") as file:
            file.write(dataBlock)

def logMessage(data):
    os.makedirs(os.path.dirname(fullPath), exist_ok=True)
    # Force List
    if isinstance(data, str):
        data = [data]

    dataBlock : str = ""
    for entry in data:
        timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]
        dataBlock += f"{timestamp} - {entry}\n"

    with open(fullPath, "a", encoding="utf-8") as file:
        file.write(dataBlock)