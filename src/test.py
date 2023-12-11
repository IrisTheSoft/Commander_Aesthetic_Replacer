from wows_io import *


io = WowsIo(PTH.Path("F:/SteamLibrary/steamapps/common/World of Warships/bin/7814610"))
print("AVAILABLE LANGUAGES:")
print(*io.list_languages())
print("AVAILABLE VOICE OVERS:")
print(*io.list_voice_overs())
