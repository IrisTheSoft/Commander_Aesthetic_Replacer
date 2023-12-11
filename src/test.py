from wows_io import *


io = WowsIo(PTH.Path("F:/SteamLibrary/steamapps/common/World of Warships/bin/7814610"))
io.unpack(PTH.Path("gui", "crew_commander", "base", "*"))
