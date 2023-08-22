#!/usr/bin/python3.11
# -*- coding: utf-8 -*-

import os
import json
import sys
import re
import smtplib
from cryptography.fernet import Fernet
from datetime import datetime as dt
from crontab import CronTab


class Mail:

    def __init__(self, mail_sfile_dir):
        self.mail_sfile = os.path.join(mail_sfile_dir, "mail.json")
        self.secret = os.path.join(mail_sfile_dir, ".key.dat")

    def file(self, param="mail"):
        """Tworzy, odtwarza i czyta plik konfiguracji maila.

        :param param: String: "mail", "user", "pass", "server"
        :return: None lub String
        """
        mail_data_structure = {"mailer": ["mailaddr", "mailuser", "mailpass", ["server", "port", "ssl"]]}
        if not os.path.exists(self.mail_sfile):
            with open(self.mail_sfile, "w") as f:
                json.dump(mail_data_structure, f, indent=4)
        else:
            try:
                with open(self.mail_sfile, "r") as f:
                    data = json.load(f)
                if (len(list(data)) != len(mail_data_structure) or
                        len(data.values()) != len(mail_data_structure.values())):
                    with open(self.mail_sfile, "w") as f:
                        json.dump(mail_data_structure, f, indent=4)
            except json.decoder.JSONDecodeError:
                with open(self.mail_sfile, "w") as f:
                    json.dump(mail_data_structure, f, indent=4)

        with open(self.mail_sfile, "r") as f:
            data = json.load(f)
        if param == "mail":
            return data["mailer"][0]
        elif param == "user":
            return data["mailer"][1]
        elif param == "pass":
            return data["mailer"][2]
        elif param == "server":
            return data["mailer"][3]

    def send(self, quantity):
        """Wysyła wiadomość email informującą o ilości usuniętych plików."""
        import socket

        # Dekodowanie zaszyfrowanego hasła:
        with open(self.secret, "r") as f:
            key = bytes.fromhex(f.read())
        decoded_password = Fernet(key).decrypt(bytes.fromhex(self.user_password)).decode()

        mail_from = info("title")
        mail_to = self.user_mail
        mail_subject = "Usunieto: {} plikow.".format(quantity)
        mail_body = ("""
Nazwa hosta: {}
Wykonanie zakonczone w dniu {} o godzinie {:.8s}"""
                     .format(socket.gethostname(), dt.now().date(), dt.now().time().isoformat()))

        message = """From: {}
To: {}
Subject: {}

{}
""".format(mail_from, mail_to, mail_subject, mail_body)

        # Wykonanie:
        try:
            if self.smtp_server[2]:
                server = smtplib.SMTP_SSL(self.smtp_server[0], self.smtp_server[1])
            else:
                server = smtplib.SMTP(self.smtp_server[0], self.smtp_server[1])
            server.ehlo()
            server.login(self.user_login, decoded_password)
            server.sendmail(self.user_login, mail_to, message)
            server.close()
        except Exception as error:
            print("Sending error: {}".format(error))

    @property
    def user_mail(self):
        # Własność adresu email.
        if self.file("mail") == "mailaddr":
            return None
        else:
            return self.file("mail")

    @user_mail.setter
    def user_mail(self, value):
        # Ustawianie adresu email.
        with open(self.mail_sfile, "r") as f:
            data = json.load(f)
        data["mailer"][0] = value
        with open(self.mail_sfile, "w") as f:
            json.dump(data, f, indent=4)

    @property
    def user_login(self):
        # Własność loginu.
        if self.file("user") == "mailuser":
            return None
        else:
            return self.file("user")

    @user_login.setter
    def user_login(self, value):
        # Ustawianie loginu.
        with open(self.mail_sfile, "r") as f:
            data = json.load(f)
        data["mailer"][1] = value
        with open(self.mail_sfile, "w") as f:
            json.dump(data, f, indent=4)

    @property
    def smtp_server(self, param="default"):
        # Własność adresu serwera smtp, jego portu i wymagalności SSL.
        if self.file("server") == ["server", "port", "ssl"]:
            return None
        else:
            server, port, ssl = self.file("server")
            return [server, int(port), bool(ssl)]

    @smtp_server.setter
    def smtp_server(self, value):
        """Ustawianie adresu serwera smtp i jego portu.

        :param value: List ["server", "port", "ssl"]
        server: adres serwera smtp
        port: port serwera smtp
        ssl: True lub False
        """
        with open(self.mail_sfile, "r") as f:
            data = json.load(f)
        data["mailer"][3] = value
        with open(self.mail_sfile, "w") as f:
            json.dump(data, f, indent=4)

    @property
    def user_password(self):
        # Własność zaszyfrowanego hasła.
        if self.file("pass") == "mailpass":
            return None
        else:
            with open(self.secret, "r") as f:
                return self.file("pass")

    @user_password.setter
    def user_password(self, value):
        # Ustawianie i szyfrowanie hasła.
        with open(self.mail_sfile, "r") as f:
            data = json.load(f)
        klucz = Fernet.generate_key()   # Wygeneruj klucz.
        with open(self.secret, "w") as f:    # Zapisz klucz w ukrytym pliku.
            f.write(klucz.hex())
        data["mailer"][2] = Fernet(klucz).encrypt(value.encode()).hex()    # Zaszyfruj i przekaż hasło do słownika.
        with open(self.mail_sfile, "w") as f:       # Zrzuć zaszyfrowane hasło do pliku mail.json
            json.dump(data, f, indent=4)


def info(param="read"):
    """Zwraca informacje na temat programu lub konkretną informację.

    :param param: str: "title", "author", "version"
    :return: str
    """
    inf = {
        "title":  "CamSnapshotManager",
        "author": "Paweł Gabryś",
        "version": "2.5"
    }

    txt = """{}
Autor: {}
Program do zarządzania ujęciami z kamery CCTV.
Pozwala na ustawianie czasu po jakim pliki zdjęć mają zostać usunięte.
Obsługuje powiadomienia email.
    
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
    """Funkcja operowania na pliku ustawień.

    :param param: String: "check", "create", "modify", "paths_quantity"
    :param _index: Integer
    :param kwargs: active=boolean, timespan=str, path=str
    :return: int lub str lub boolean
    """
    set_list = ["active", "timespan", "mailer", "path"]
    param_list = ["check", "create", "modify", "paths_quantity"]

    def file_check():
        # Czy plik istnieje
        if os.path.exists(sfile):
            with open(sfile, "r") as f1:
                # Czy podstawowa struktura jest poprawna
                try:
                    data_check = json.load(f1)
                    if len(data_check[_index]) == len(set_list[:3]):
                        return True
                    else:
                        return False
                except json.decoder.JSONDecodeError:
                    return False
        else:
            return False

    # Wykonaj operację zależnie od argumentu:
    if param == param_list[0]:
        return file_check()
    elif param == param_list[1]:
        # Tworzenie pliku konfiguracyjnego
        with open(sfile, "w") as f:
            # Domyślna zawartość pliku ustawień:
            settings = [{set_list[0]: False, set_list[1]: "90d", set_list[2]: False}, {set_list[3]: ""}]
            json.dump(settings, f, indent=4)
    else:
        if file_check():
            with open(sfile, "r") as f:
                data = json.load(f)

                if param == param_list[2]:
                    # Modyfikuje zawartość pliku.
                    for key, value in kwargs.items():
                        if key in set_list:
                            data[_index][key] = value
                            with open(sfile, "w") as nf:
                                print(data)
                                json.dump(data, nf, indent=4)
                elif param == param_list[3]:
                    # Zwraca ilość zdefiniowanych ścieżek.
                    return len(list(data[1:]))
                elif param in set_list[0:4]:
                    # Zwraca klucz lub wartość klucza, zależnie od parametru.
                    return data[(_index + 1 if param == set_list[3] else _index)][param]


def timespan_values(value):
    """ Przelicza wartości z sufiksami na sekundy.

    :param value: String: liczba z sufiksem 'h' lub 'd'
    :return: Integer
    """
    time, mod = re.split(r'(\d+)', value)[1:3]      # Wyrażenie regularne do rozdzielania liczby od sufiksu.

    if mod == "h":
        return int(time) * 60 * 60      # Godziny na sekundy.
    elif mod == "d":
        return int(time) * 60 * 60 * 24     # Dni na sekundy.


def execute():
    """Wykonanie operacji na plikach."""
    file_num = 0    # Zmienna do liczenia ilości usuniętych plików.
    executed = False

    with open(sfile, "r") as f:
        data = json.load(f)
    indexes = list(range(1, len(list(data[1:])) + 1))       # Określanie wartości ścieżki docelowej w pliku ustawień.
    now = dt.now().timestamp()      # Aktualny czas w formie znacznika czasu.

    for path_index in indexes:
        fpath = data[path_index]["path"]
        fspan = timespan_values(settings_file("timespan"))

        for file1 in os.listdir(fpath):     # Iteracja przez pliki w docelowej lokalizacji.
            filepath = os.path.join(fpath, file1)
            time_diff = now - os.path.getctime(filepath)        # Obliczanie różnicy czasu.
            if os.path.isfile(filepath):
                if time_diff >= fspan:
                    # Jeżeli różnica czasu wynosi więcej, niż zdefiniowana w ustawieniach, plik zostaje usunięty.
                    file_num += 1
                    executed = True
                    os.remove(filepath)

    if executed:
        mailing("send", file_num)


def set_path(param="check"):
    """Funkcja ustawiania i sprawdzania ścieżki folderu docelowego.

    :param param: String: "check", "set"
    :return: boolean lub None
    """
    param_list = ["check", "set"]

    def path_check(path="", index=1):
        """Sprawdzanie, czy folder docelowy istnieje.

        :param path: String
        :param index: Integer >= 1
        :return: boolean
        """
        if path == "":
            return os.path.exists(data[index]["path"])
        else:
            return os.path.exists(path)

    def path_set(index=1, *manage_path):
        """Ustawianie wartości kluczy "path" w pliku ustawień.

        :param index: Integer >= 1
        :param manage_path: String: "a" dodawanie lub "d" - usuwanie
        """
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
        """Zarządzanie ścieżką po jej wyborze.

        :param choice: Integer: numer indeksu odnoszący się do danej ścieżki w pliku ustawień.
        """
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
                # Wybór spośród zapisanych ścieżek.
                manage(int(u_in))
            elif u_in == "+":   # Dodawanie nowej ścieżki.
                path_set(settings_file("paths_quantity"))
            elif u_in == "":       # Pusty wybór pozwala na powrót do poprzedniego menu.
                break
            else:
                print("\nSpróbuj ponownie.\n")


def set_time():
    """Ustawianie maksymalnego "wieku" plików do usunięcia."""
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

    if u_in == "":  # Pusty wybór pozwala na powrót do poprzedniego menu.
        return
    else:
        try:
            time, mod = re.split(r'(\d+)', u_in)[1:]    # Wyrażenie regularne do rozdzielania liczby od sufiksu.
            if time.isdigit():
                if mod == "h" or mod == "d":
                    settings_file("modify", timespan=u_in)
                    print("Pomyślnie zmieniono wartość.")
                else:
                    print("Błąd. Błędny sufiks.")
        except ValueError:
            print("Błąd. Błędna wartość.")


def switch():
    """Przełączenie automatyzacji procesu za pomocą menedżera Cron."""
    def cron_man(param, *time):
        """Edytowanie CronTab.

        :param param: String: "a" by dodać, "r" by usunąć
        :param time: String: "hh:mm"
        """
        param_list = ["a", "r"]
        # Pobierz nazwę użytkownika uruchamiającego program i użyj jego Crontaba:
        cron = CronTab(user=os.getlogin())
        command = "/usr/bin/python3.11 {} -x".format(pfile)     # Polecenie ze zdefiniowaną wersją interpretera.
        if param == param_list[0]:  # Dodaj do Crontab:
            stime = str(time[0]).split(":")     # Rozdzielanie godzin i minut
            job = cron.new(command=command)
            job.setall("{} {} * * *".format(stime[1], stime[0]))   # Czas wykonania
            cron.write()
        elif param == param_list[1]:    # Usuń z Crontab:
            for job in cron:
                if job.command == command:
                    cron.remove(job)
            cron.write()

    if settings_file() and settings_file("active") == "On":     # Odczyt stanu z pliku konfiguracyjnego.
        if set_path():
            settings_file("modify", active="Off")
            cron_man("r")
        else:
            # Rezultat próby aktywacji bez zdefiniowanego folderu.
            txt = "Brak ścieżki do folderu. Skonfiguruj ścieżkę."
            print("\n{0}\n{1}\n{0}".format("-" * len(txt), txt))
            set_path("set")
    else:
        u_in = input("Wprowadź czas (hh:mm) uruchomienia programu: ")

        settings_file("modify", active="On")
        cron_man("a", u_in)


def mailing(param="addr", *quantity):
    """Pozwala ustawić system wysyłania powiadomień email.

    :param param: String: "addr" - zwraca ustawiony email, "set"
    :return: String lub None
    """
    params = ["addr", "set", "send"]
    msg = Mail(program_dir)
    msg.file()

    # Sprawdź parametr:
    if param == params[0]:
        return msg.user_mail
    elif param == params[1]:
        if settings_file("mailer"):
            settings_file("modify", mailer=False)
        else:
            all_good = False
            while not all_good:     # Pętla poprawnej kombinacji serwer_smtp:port.
                server_and_port = input("""
Podaj adres serwera smtp i port (adres:port). 
[Enter] by powrócić: """)
                if server_and_port == "":
                    break
                else:
                    # Czy format jest błędny lub port nie jest liczbą całkowitą:
                    if len(server_and_port.split(":")) != 2 or not server_and_port.split(":")[1].isdigit():
                        print("Spróbuj ponownie.")
                        continue
                    ssl = input("SSL ([tak] lub [nie]: ")   # Zapytanie o protokół SSL.
                    if ssl.lower() == "tak":
                        ssl = "Yes"
                    elif ssl.lower() == "nie":
                        ssl = "No"
                    else:
                        print("Spróbuj ponownie.")
                        continue
                # Formatowanie i zapis parametru:
                msg.smtp_server = [server_and_port.split(":")[0], server_and_port.split(":")[1], ssl]
                all_good = True

            login = input("Login konta email: ")    # Ustawianie parametru loginu.
            if login != "":
                msg.user_login = login

            pwd = input("Hasło konta email: ")      # Ustawianie parametru hasła i przekazanie do szyfrowania i zapisu.
            if pwd != "":
                msg.user_password = pwd
                keydir = os.path.join(program_dir, ".key.dat")
                mset = os.path.join(program_dir, "mail.json")
                with open(keydir, "r") as f:
                    key = bytes.fromhex(f.read())
                with open(mset, "r")as f:
                    dane = json.load(f)
                haselko = dane["mailer"][2]
                print(Fernet(key).decrypt(bytes.fromhex(haselko)).decode())

            all_good = False
            while not all_good:     # Pętla poprawności formatu adresu email.
                email = input("""
Wprowadź adres email do otrzymywania powiadomień: 
[Enter] by powrócić: """)
                podzielony = email.split("@")
                if email == "":
                    break
                elif len(podzielony) != 2 or len(podzielony[1].split(".")) < 2:
                    print("Spróbuj ponownie.")
                    continue
                else:
                    msg.user_mail = email
                    settings_file("modify", mailer=True)
                    all_good = True
    elif param == params[2]:
        msg.send(int(quantity[0]))


def main():
    """Kod główny, zdefiniowany w funkcji na potrzeby obsługi uruchamiania programu z parametrami uruchomieniowymi."""
    while True:
        if not os.path.exists(sfile):
            settings_file("create")
        operation = "Wyłącz" if settings_file("active") is True else "Włącz"    # Przełącznik automatyzacji.
        mailer = "Wyłącz" if settings_file("mailer") is True else "Włącz"  # Przełącznik mailera.
        main_opt = {"1": f"{operation} automatyzację", "2": "Wskaż ścieżki do folderów",
                    "3": "Zmień okres przechowywania zdjęć", "4": f"{mailer} mailer", "x": "Wyjście"}     # Lista opcji.
        opts = list(main_opt)

        txt = """
{0}
{1}
{0}

Automatyzacja: {2}
Mailer: {3}
Czas przechowywania: {4}
""".format("-" * len(info("title")), info("title"),
            "Wyłączona" if not settings_file("active") is True else "Włączona",
           "Nieaktywny" if not settings_file("mailer") is True else mailing(), settings_file("timespan"))
        print(txt)
        for opt, desc in main_opt.items():
            if opt == opts[4]:
                print("{}\n[{}] - {}".format("-" * len(info("title")), opt, desc))
            else:
                print("[{}] - {}".format(opt, desc))

        u_in = input("\nWybierz opcję i zatwierdź klawiszem [Enter]: ")

        if u_in not in str(list(main_opt)):
            print("Spróbuj ponownie.")
        elif u_in == opts[4]:
            break
        elif u_in == opts[3]:
            mailing("set")
        elif u_in == opts[2]:
            set_time()
        elif u_in == opts[1]:
            set_path("set")
        elif u_in == opts[0]:
            switch()


# Główne zmienne:
program_dir = os.path.dirname(os.path.abspath(__file__))
pfilename = os.path.basename(os.path.abspath(sys.argv[0]))
sfile = os.path.join(program_dir, "settings.json")
pfile = os.path.join(program_dir, pfilename)

# Obsługa parametrów uruchomieniowych:
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
