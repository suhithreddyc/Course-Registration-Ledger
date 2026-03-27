import json, os

_base = os.path.dirname(__file__)
_dep  = json.load(open(os.path.join(_base, "deployment.json")))

GANACHE_URL       = "http://127.0.0.1:7545"
CONTRACT_ADDRESS  = _dep["contractAddress"]
ADMIN_ADDRESS     = _dep["adminAddress"]

# ── Paste Account[0] private key from Ganache UI here ──
# How to find it: Ganache → click the 🔑 key icon on Account[0] row
ADMIN_PRIVATE_KEY = "0x4dad00d26bf328019b0f71c250dc1be80d56d09410a5e88e77ff2d5bef758328"