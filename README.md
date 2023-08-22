# CamSnapshotManager
Program do zarządzania ujęciami z kamery CCTV.
Pozwala na ustawianie czasu po jakim pliki zdjęć mają zostać usunięte.
Pozwala wysyłać powiadomienia email o ilości usuniętych plików.

Jako że program de facto zarządza plikami w określonym folderze, można go wykorzystać również do innych celów, np. usuwanie przestarzałych plików .log


Wykorzystane moduły:

-os,

-json,

-sys,

-re,

-datetime,

-smtplib

-crontab:

    pip install python-crontab

-cryptography:

    pip install cryptography
    
Parametry:

        [-h] wyświetla pełne informacje o programie,
        [-x] wykonuje skrypt z pomocą zapisanych ustawień,
        [-m] wyświetla menu programu,
        [-v] wyświetla wersję programu,
        [-i] wyświetla skrócone informacje o programie
