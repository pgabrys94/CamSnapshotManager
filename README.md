# CamSnapshotManager
Program do zarządzania ujęciami z kamery CCTV.
Pozwala na ustawianie czasu po jakim pliki zdjęć mają zostać usunięte.

Jako że program de facto zarządza plikami w określonym folderze, można go wykorzystać również do innych celów, np. usuwanie przestarzałych plików .log


Wykorzystane moduły:

-os,

-json,

-sys,

-re,

-datetime,

-crontab:

    pip install python-crontab
    
Parametry:

        [-h] wyświetla informacje o programie,
        [-x] wykonuje skrypt z pomocą zapisanych ustawień,
        [-m] wyświetla menu programu.
