#!/usr/bin/python3.11
# -*- coding: utf-8 -*-

import os
import json
import sys
import re
from datetime import datetime as dt
from crontab import CronTab


def info(param="read"):
    inf = {
        "title":  "CamSnapshotManager",
        "author": "Paweł Gabryś",
        "version": "2.1"
    }

    txt = """{}
Autor: {}
Program do zarządzania ujęciami z kamery CCTV.
Pozwala na ustawianie czasu po jakim pliki zdjęć mają zostać usunięte.
    
Parametry:
    [-h] wyświetla informacje o programie,
    [-x] wykonuje skrypt z pomocą zapisanych ustawień,
    [-m] wyświetla menu programu,
    [-v] wyświetla wersję programu
    [-i] wyświetla wszystkie podstawowe informacje""".format(inf["title"], inf["author"], inf["version"])

    if param == "read":
        print(txt)
    else:
        return inf[param]


def settings_file(param="check", _index=0, **kwargs):
    set_list = ["active", "timespan", "path"]
    param_list = ["check", "create", "modify", "paths_quantity"]

    def file_check():
        if os.path.exists(sfile):
            with open(sfile, "r") as f1:
                try:
                    data_check = json.load(f1)
                    if len(data_check[_index]) == len(set_list[:2]):
                        return True
                    else:
                        return False
                except json.decoder.JSONDecodeError:
                    return False
        else:
            return False

    if param == param_list[0]:
        return file_check()
    elif param == param_list[1]:
        with open(sfile, "w") as f:
            settings = [{set_list[0]: "False", set_list[1]: "90d"}, {set_list[2]: ""}]
            json.dump(settings, f, indent=4)
    else:
        if file_check():
            with open(sfile, "r") as f:
                data = json.load(f)

                if param == param_list[2]:
                    for key, value in kwargs.items():
                        if key in set_list:
                            data[_index][key] = value
                            with open(sfile, "w") as nf:
                                json.dump(data, nf, indent=4)
                elif param == param_list[3]:
                    return len(list(data[1:]))
                elif param in set_list[0:4]:
                    return data[(_index if param != set_list[2] else _index + 1)][param]


def timespan_values(value):
    time, mod = re.split(r'(\d+)', value)[1:3]

    if mod == "h":
        return int(time) * 60 * 60
    elif mod == "d":
        return int(time) * 60 * 60 * 24


def execute():
    with open(sfile, "r") as f:
        data = json.load(f)

    print("Rzeczywista ilość ścieżek:", len(list(data[1:])))
    indexes = list(range(1, len(list(data[1:])) + 1))
    print("Lista indeksów:", indexes)
    for path_index in indexes:
        print("Lista indeksów w pętli:", indexes)
        print("Wartość i typ iterowanego indeksu:", path_index, type(path_index))
        fpath = data[path_index]["path"]
        print("Ścieżka do folderu: {}".format(fpath))
        fspan = timespan_values(settings_file("timespan"))
        print("Maksymalny wiek w (s): {}".format(fspan))
        print("Liczba plików w podanej lokalizacji: {}".format(len(os.listdir(fpath))))


def set_path(param="check"):
    param_list = ["check", "set"]

    def path_check(path="", index=1):
        if path == "":
            return os.path.exists(data[index]["path"])
        else:
            return os.path.exists(path)

    def path_set(index=1, *manage_path):

        if "d" in manage_path:
            print("Usunięto ścieżkę: '{}'".format(data[index]["path"]))
            data.pop(index)
            if len(data) < 2:
                data.append({"path": ""})
            with open(sfile, "w") as f1:
                json.dump(data, f1, indent=4)
        else:
            path_u_in = input("Wprowadź pełną ścieżkę do folderu: ")

            if path_check(path_u_in) and path_u_in != "":
                if data[index]["path"] == "":
                    data[index]["path"] = path_u_in
                elif data[index]["path"] != "" and "a" in manage_path:
                    data[index]["path"] = path_u_in
                else:
                    data.append({"path": path_u_in})
                    index += 1
                with open(sfile, "w") as f1:
                    json.dump(data, f1, indent=4)
                print("Pomyślnie zapisano ścieżkę: '{}'".format(data[index]["path"]))
            else:
                err = "Błąd. Ścieżka nie istnieje."
                print("\n{0}\n{1}\n{0}".format("-" * len(err), err))

    def manage(choice):
        options = {"1": "Edytuj", "2": "Usuń"}
        while True:
            print("Ścieżka: '{}'".format(data[choice]["path"]))
            for opt in options:
                print("[{}] - {}".format(opt, options[opt]))

            u_in_manage = input("Wybór ([Enter] by powrócić): ")

            if u_in_manage.isdigit() and u_in_manage in list(options):
                if u_in_manage == "1":
                    path_set(int(choice), "a")
                elif u_in_manage == "2":
                    path_set(int(choice), "d")
                    break
            elif u_in_manage == "":
                break
            else:
                "\nSpróbuj ponownie.\n"

    with open(sfile, "r") as f:
        data = json.load(f)

    if param == param_list[0]:
        return path_check()
    if param == param_list[1]:
        while True:
            txt = ["\nZarządzaj ścieżką:", "[+] - nowa ścieżka...", "<brak ścieżek>"]

            print(txt[0])
            if data[1]["path"] == "":
                print(txt[2])
            else:
                for ind in list(range(1, settings_file("paths_quantity") + 1)):
                    print("[{}] - '{}'".format(ind, data[ind]["path"]))
            print("-" * len(txt[0]), "\n{}".format(txt[1]))

            u_in = input("Wybór ([Enter] by powrócić): ")
            if u_in.isdigit() and int(u_in) in list(range(1, settings_file("paths_quantity") + 1)):
                manage(int(u_in))
            elif u_in == "+":
                path_set(settings_file("paths_quantity"))
            elif u_in == "":
                break
            else:
                print("\nSpróbuj ponownie.\n")


def set_time():
    txt = """
Obsługiwane sufiksy:
    h - godziny
    d - dni

Przykład: 72h - 72 godziny, 90d - 90 dni
Domyślnie: 90d   
"""
    print(txt)
    u_in = input("Wprowadź wartość z sufiksem i zatwierdź klawiszem [Enter]: ")
    u_in = u_in.lower()

    if u_in == "":
        return
    else:
        try:
            time, mod = re.split(r'(\d+)', u_in)[1:]
            if time.isdigit():
                if mod == "h" or mod == "d":
                    settings_file("modify", timespan=u_in)
                    print("Pomyślnie zmieniono wartość.")
                else:
                    print("Błąd. Błędny sufiks.")
        except ValueError as kurwa:
            print("Błąd. Błędna wartość.", kurwa)


def switch():
    def cron_man(param, *time):
        param_list = ["a", "r"]
        cron = CronTab(user=os.getlogin())
        command = "/usr/bin/python3.11 {} -x".format(pfile)
        if param == param_list[0]:
            stime = str(time[0]).split(":")
            job = cron.new(command=command)
            job.setall("{} {} * * *".format(stime[1], stime[0]))
            cron.write()
        elif param == param_list[1]:
            for job in cron:
                if job.command == command:
                    cron.remove(job)
            cron.write()

    if settings_file("active") and settings_file():
        if set_path():
            settings_file("modify", active=False)
            cron_man("r")
        else:
            txt = "Brak ścieżki do folderu. Skonfiguruj ścieżkę."
            print("\n{0}\n{1}\n{0}".format("-" * len(txt), txt))
            set_path("set")
    else:
        u_in = input("Wprowadź czas (hh:mm) uruchomienia programu: ")

        settings_file("modify", active=True)
        cron_man("a", u_in)


def main():
    while True:
        if not os.path.exists(sfile):
            settings_file("create")
        operation = "Wyłącz" if settings_file("active") is True else "Włącz"
        main_opt = {"1": f"{operation}", "2": "Wskaż ścieżki do folderów", "3": "Zmień okres przechowywania zdjęć",
                    "4": "Wyjście"}
        opts = list(main_opt)

        txt = """
{0}
{1}
{0}

Status: {2}
Czas przechowywania: {3}
""".format("-" * len(info("title")), info("title"),
            "Wyłączony" if not settings_file("active") is True else "Włączony", settings_file("timespan"))
        print(txt)
        for opt, desc in main_opt.items():
            print("[{}] - {}".format(opt, desc))

        u_in = input("\nWybierz opcję i zatwierdź klawiszem [Enter]: ")

        if u_in not in str(list(main_opt)):
            print("Spróbuj ponownie.")
        elif u_in == opts[3]:
            break
        elif u_in == opts[2]:
            set_time()
        elif u_in == opts[1]:
            set_path("set")
        elif u_in == opts[0]:
            switch()


program_dir = os.path.dirname(os.path.abspath(__file__))
pfilename = os.path.basename(os.path.abspath(sys.argv[0]))
sfile = os.path.join(program_dir, "settings.json")
pfile = os.path.join(program_dir, pfilename)

if len(sys.argv) == 2 and sys.argv[1] == "-x" and settings_file():
    execute()
elif len(sys.argv) == 2 and (sys.argv[1] == "-x" or sys.argv[1] == "-m") and not settings_file():
    text = "Brak pliku konfiguracyjnego lub uszkodzony plik - SKONFIGURUJ PROGRAM"
    print("\n{0}\n{1}\n{0}".format("-" * len(text), text))
    settings_file("create")
    main()
elif len(sys.argv) == 2 and sys.argv[1] == "-m" and settings_file():
    main()
elif len(sys.argv) == 2 and sys.argv[1] == "-h":
    info()
elif len(sys.argv) == 2 and sys.argv[1] == "-v":
    print(info("version"))
elif len(sys.argv) == 2 and sys.argv[1] == "-i":
    print(info("title"), "v" + info("version"), "by", info("author"))
else:
    print("Błąd. Użyj parametru -h aby uzyskać listę opcji.")
