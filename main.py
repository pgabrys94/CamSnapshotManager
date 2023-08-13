import os
import json
from datetime import datetime as dt
import sys


def info():
    text = """CamSnapshotManager
    Autor: Paweł Gabryś
    Program zarządzania ujęciami z kamery CCTV.
    Pozwala na ustawianie czasu po jakim pliki zdjęć mają zostać usunięte.
    
    Parametry:
        [-h] wyświetla informacje o programie,
        [-x] wykonuje skrypt z pomocą zapisanych ustawień,
        [-m] wyświetla menu programu."""
    print(text)


def settings_file(param="check", **kwargs):
    program_dir = os.path.dirname(os.path.abspath(__file__))
    file = os.path.join(program_dir, "settings.json")
    set_list = ["active", "path", "timespan"]
    param_list = ["check", "create", "modify"]

    if param == param_list[0]:
        if os.path.exists(file):
            with open(file, "r") as f:
                data = json.load(f)
                if len(data) == len(set_list):
                    return True
                else:
                    return False
        else:
            return False
    elif param == param_list[1]:
        settings = {set_list[0]: "False", set_list[1]: "", set_list[2]: ""}
        with open(file, "w") as f:
            json.dump(settings, f)
    elif param == param_list[2]:
        with open(file, "r") as f:
            data = json.load(f)
        for key, value in kwargs.items():
            data[key] = value
        with open(file, "w") as f:
            json.dump(data, f)
    elif param in set_list[0:4]:
        with open(file, "r") as f:
            data = json.load(f)
            result = data[param]
        return result


def execute():
    pass


def set_path():
    pass


def set_time():
    pass


def switch():
    pass


def is_on():
    return True


def main():
    running = True
    operation = "Wyłącz" if is_on() else "Włącz"
    main_opt = {"1": f"{operation}", "2": "Wskaż lokalizację folderu", "3": "Zmień okres przechowywania zdjęć",
                "4": "Wyjście"}
    opts = list(main_opt)
    print(os.path.dirname(os.path.abspath(__file__)))

    while running:
        for opt, desc in main_opt.items():
            print("[{}] - {}".format(opt, desc))

        u_in = input("Wybierz opcję i potwierdź klawiszem [Enter]: ")

        if u_in not in str(list(main_opt)):
            print("Błąd.")
        elif u_in == opts[3]:
            break
        elif u_in == opts[2]:
            set_time()
        elif u_in == opts[1]:
            set_path()
        elif u_in == opts[0]:
            switch()


if len(sys.argv) == 2 and sys.argv[1] == "-x" and settings_file():
    execute()
elif len(sys.argv) == 2 and sys.argv[1] == "-x" and not settings_file():
    print("Brak pliku konfiguracyjnego lub uszkodzony plik - SKONFIGURUJ PROGRAM")
    main()
elif len(sys.argv) == 2 and sys.argv[1] == "-m":
    main()
elif len(sys.argv) == 2 and sys.argv[1] == "-h":
    info()
else:
    print("Błąd. użyj parametru -h aby uzyskać listę opcji")
