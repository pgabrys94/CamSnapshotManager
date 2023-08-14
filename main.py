import os
import json
import sys
import re
from datetime import datetime as dt
from crontab import CronTab


def info():
    text = """CamSnapshotManager
    Autor: Paweł Gabryś
    Program do zarządzania ujęciami z kamery CCTV.
    Pozwala na ustawianie czasu po jakim pliki zdjęć mają zostać usunięte.
    
    Parametry:
        [-h] wyświetla informacje o programie,
        [-x] wykonuje skrypt z pomocą zapisanych ustawień,
        [-m] wyświetla menu programu."""
    print(text)


def settings_file(param="check", **kwargs):
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
        settings = {set_list[0]: "False", set_list[1]: "", set_list[2]: "90d"}
        with open(file, "w") as f:
            json.dump(settings, f)
    elif param == param_list[2]:
        with open(file, "r") as f:
            data = json.load(f)
        for key, value in kwargs.items():
            if key in set_list:
                data[key] = value
        with open(file, "w") as f:
            json.dump(data, f)
    elif param in set_list[0:4]:
        with open(file, "r") as f:
            data = json.load(f)
            result = data[param]
        return result
    else:
        return "ERROR"


def timespan_values(value):
    time, mod = re.split(r'(\d+)', value)[1:3]

    if mod == "h":
        return int(time) * 60 * 60
    elif mod == "d":
        return int(time) * 60 * 60 * 24


def execute():
    now = dt.now().timestamp()
    with open(file, "r") as f:
        data = json.load(f)
        fpath = data["path"]
        fspan = timespan_values(data["timespan"])

    for file1 in os.listdir(fpath):
        filepath = os.path.join(fpath, file1)
        time_diff = now - os.path.getctime(filepath)
        if os.path.isfile(filepath):
            if time_diff >= fspan:
                os.remove(filepath)


def set_path():
    pass


def set_time():
    text = """ Obsługiwane sufiksy:
        h - godziny
        d - dni

    Przykład: 72h - 72 godziny, 90d - 90 dni   
    """
    print(text)
    u_in = input("Wprowadź wartość z sufiksem i zatwierdź klawiszem [Enter]: ")
    u_in = u_in.lower()

    time, mod = re.split(r'(\d+)', u_in)[1:3]

    if time.isdigit():
        if mod == "h" or mod == "d":
            settings_file("modify", timespan=u_in)
        else:
            print("Błąd. Błędny sufiks.")
    else:
        print("Błąd. Błędna wartość.")


def switch():
    def cron_man(param, *time):
        plist = ["a", "r"]
        cron = CronTab(user=os.getlogin())
        command = "/usr/bin/python {} -x".format(pfile)
        if param == plist[0]:
            stime = str(time[0]).split(":")
            job = cron.new(command=command)
            job.setall("{} {} * * *".format(stime[1], stime[0]))
            cron.write()
        elif param == plist[1]:
            for job in cron:
                if job.command == command:
                    cron.remove(job)
            cron.write()

    if is_on():
        settings_file("modify", active=False)
        cron_man("r")
    else:
        u_in = input("Wprowadź czas (hh:mm) uruchomienia programu: ")

        settings_file("modify", active=True)
        cron_man("a", u_in)


def is_on():
    return settings_file("active")


def main():
    operation = "Wyłącz" if is_on() else "Włącz"
    main_opt = {"1": f"{operation}", "2": "Wskaż lokalizację folderu", "3": "Zmień okres przechowywania zdjęć",
                "4": "Wyjście"}
    opts = list(main_opt)
    print(os.path.dirname(os.path.abspath(__file__)))

    while True:
        for opt, desc in main_opt.items():
            print("[{}] - {}".format(opt, desc))

        u_in = input("Wybierz opcję i zatwierdź klawiszem [Enter]: ")

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


program_dir = os.path.dirname(os.path.abspath(__file__))
pfilename = os.path.basename(os.path.abspath(sys.argv[0]))
sfile = os.path.join(program_dir, "settings.json")
pfile = os.path.join(program_dir, pfilename)

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
    print("Błąd. Użyj parametru -h aby uzyskać listę opcji.")
