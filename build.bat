pyinstaller ^
    --add-data src/voice_mod_template.xml.jinja:. ^
    --noconsole ^
    --onedir ^
    --name wows_commander_asthetic_replacer ^
    src/gui.py
copy README.md dist\wows_commander_asthetic_replacer\README.md
copy commanders.csv dist\wows_commander_asthetic_replacer\commanders.csv
copy /b wowsunpack.exe dist\wows_commander_asthetic_replacer\wowsunpack.exe
