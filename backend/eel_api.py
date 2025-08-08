# backend/eel_api.py

import eel
from backend.feature import takeAllCommands

@eel.expose
def takeAllCommandsExposed():
    return takeAllCommands()
