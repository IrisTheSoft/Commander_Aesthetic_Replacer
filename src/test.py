from wows_io import *


io = WowsIo(PTH.Path("F:/SteamLibrary/steamapps/common/World of Warships/bin/7814610"))
io.install_portraits({
    PTH.Path("Japan", "Akeno_Mashiro.png"): PTH.Path("F:/playground/akeno_mashiro_cropped.png"),
    PTH.Path("Germany", "Mina_Thea.png"): PTH.Path("F:/playground/thea_wilhelmina_cropped.png")})
io.install_names({
    "IDS_AKENO_MASHIRO": "Akeno & Mashiro",
    "IDS_MINA_THEA": "Thea & Wilhelmina"},
    "es_mx")
