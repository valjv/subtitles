import datetime
import chardet
from simple_term_menu import TerminalMenu
from os import listdir
from os.path import isfile, join

def detect_encoding(filename):
    with open(filename, "rb") as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        return result["encoding"]

def read_file_with_encoding(filename):
    encoding = detect_encoding(filename)

    if encoding is None:
        raise ValueError("Impossible de détecter l'encodage du fichier.")
    with open(filename, "r", encoding=encoding, errors="replace") as f:
        content = f.readlines()

    return content

def time_difference(timecode: datetime.datetime, operation: str, timediff: datetime.timedelta):
    """take subtitle file timecode like 00:04:04,755
                                   ^hour ^minute ^second ^microsecond
    and the operation (adding or removing time)
    and lastly the timediff datetime.timedelta(0,3,500,0)
                                            ^hour ^minute ^second ^microsecond
    """
    if operation == "+":
        return timecode + timediff
    else:
        return timecode - timediff

def split_and_transform(timecode: str) -> datetime.datetime:
    """take the timecode from the subtitle file (in str format) and turn it into a datetime.datetime class"""
    return datetime.datetime(100,1,1, int(timecode.split(':')[0]), int(timecode.split(':')[1]),int((timecode.split(':')[2]).split(',')[0]),int(timecode.split(',')[1]) * 1000)

def ask_operation():
    options = ["[+] Ajouter du délai", "[-] Avancer les sous titre"]
    terminal_menu = TerminalMenu(options, title="Que voulez-vous faire")
    menu_entry_index = terminal_menu.show()
    print("Opération selectionné : ", options[menu_entry_index])
    return "+" if menu_entry_index == 0 else "-"

def which_file():
    """list all .srt files not starting with clean (to prevent work on already cleaned srt files) and display them via simpletermmenu"""
    onlyfiles = [f for f in listdir(".") if isfile(join(".", f))]
    srt_files = [f for f in onlyfiles if f.endswith(".srt") and not f.startswith("clean")]

    if not srt_files:
        print("Aucun fichier .srt disponible.")
        exit()

    terminal_menu = TerminalMenu(srt_files, title="Quel fichier voulez-vous utiliser?")
    menu_entry_index = terminal_menu.show()
    print("Fichier selectionné : ", srt_files[menu_entry_index])
    return srt_files[menu_entry_index]

FILE = which_file()
OPERATION = ask_operation()

lines = read_file_with_encoding(FILE)

cleansrt = open(f'clean{FILE}', 'w', encoding="utf-8")

try:
    secondes = int(input("Combien de secondes: "))
except ValueError:
    secondes = 0
try:
    millisecondes = int(input("Attention le chiffre ici est à indiquer en centaine (ex 500, 850)\nCombien de microsecondes: "))
    microsecondes = millisecondes * 1000
except ValueError:
    microsecondes = 0

for line in lines:
    if '-->' in line:
        startsub, endsub = line.split('-->')
        newstart = time_difference(split_and_transform(startsub), OPERATION, datetime.timedelta(seconds=secondes,microseconds=microsecondes))
        newend = time_difference(split_and_transform(endsub), OPERATION, datetime.timedelta(seconds=secondes,microseconds=microsecondes))
        line = f"{newstart.strftime('%H:%M:%S')},{newstart.microsecond // 1000} --> {newend.strftime('%H:%M:%S')},{newend.microsecond // 1000}\n"
    cleansrt.writelines(line)

cleansrt.close()
print(f"Fichier enregistré : clean{FILE}")