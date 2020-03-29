import settings
import subprocess
import platform
import numpy as np
import speech_recognition as sr
import time
import pyautogui as g

custom_keys = {
    "pipe": "|",
    "or": "|",
    "at": "@",
    "dollarsign": "$",
    "opensquarebracket": "[",
    "closesquarebracket": "]",
    "openparentheses": "(",
    "closeparentheses": ")",
    "dot": ".",
    "period": ".",
    "point": ".",
    "exclamationmark": "!",
    "questionmark": "?",
    "equals": "=",
    "greaterthan": ">",
    "lessthan": "<",
    "backslash": "\\",
    "slash": "/",
    "caret": "^",
    "carrot": "^",
    "ampersand": "&",
    "and": "&",
    "percent": "%",
    "percentsign": "%",
    "hash": "#",
    "pound": "#",
    "hashtag": "#",
    "tilde": "~",
    "tilda": "~",
    "backquote": "`",
    "dash": "-",
    "hyphen": "-",
    "minus": "-",
    "underscore": "_",
    "plus": "+",
    "opencurlybrace": "{",
    "closecurlybrace": "}",
    "semicolon": ";",
    "colon": ":",
    "comma": ",",
    "apostrophe": "'",
    "quote": "\"",
    "quotationmark": "\"",
    "doublequote": "\"",
    "singlequote": "\'",
    "star": "*",
    "asterisk": "*",
    "space": " ",
    "spacebar": " ",
    "return": "\r",
    "newline": "\n",
    "enter": "\n"
}

def press_key(key, cmd=g.press):
    slug = key.replace(" ", "").lower()
    if slug in custom_keys:
        key_symbol = custom_keys[slug]
        cmd(key_symbol)
    elif slug in g.KEY_NAMES:
        cmd(slug)
    else:
        print("Key not found: ", key)

def speech_to_text(typing_on, launcher_on):
    r = sr.Recognizer()
    m = sr.Microphone()
    with m as source:
        r.adjust_for_ambient_noise(source)
        while True:
            audio = r.listen(source)
            process_audio(r, audio, typing_on, launcher_on)

def process_audio(r, audio, typing_on, launcher_on):
    import main
    import webbrowser
    import os
    import start_menu

    typewrite_lengths = []

    try:
        text = r.recognize_google_cloud(audio, credentials_json=open("google-credentials.json").read()).strip()
    except sr.UnknownValueError:
        return
    
    print(f'Microphone received: "{text}"')
    lower = text.lower()

    if typing_on:
        if lower.startswith("type "):
            _, rest = text.split(" ", maxsplit=1)
            g.typewrite(rest)
            typewrite_lengths.append(len(rest))
        
        # keyboard shortcuts
        if lower == 'undo':
            g.hotkey('ctrl', 'z')
        elif lower == 'copy':
            g.hotkey('ctrl', 'c')
        elif lower == 'paste' or lower == 'pace':
            g.hotkey('ctrl', 'v')
        elif lower == 'cut':
            g.hotkey('ctrl', 'x')
        elif lower == 'undo typing':
            if typewrite_lengths:
                g.press("backspace", typewrite_lengths[-1])
                typewrite_lengths = typewrite_lengths[:-1]
        elif lower.replace(" ", "") == 'fullscreen':
            g.press('f11')

        # key controls
        if lower.startswith("press "):
            key = lower[6:]
            press_key(key)
        elif lower.startswith("hold "):
            key = lower[5:]
            press_key(key, cmd=g.keyDown)
        elif lower.startswith("release "):
            key = lower[8:]
            press_key(key, cmd=g.keyUp)

        # hotkey shortcuts
        elif "control" in lower or "shift" in lower or "ctrl" in lower or "alt" in lower or "windows" in lower:
            keys = lower.split()
            keys = ["ctrl" if key=="control" else key for key in keys]
            g.hotkey(*keys)
        elif lower.replace(" ", "") in custom_keys:
            g.press(custom_keys[lower.replace(" ", "")])
        elif lower.replace(" ", "") in g.KEY_NAMES:
            g.press(lower.replace(" ", ""))
    
    # recalibrate the tracker
    if "calibrate" in lower:
        if settings.tracker_active:
            print("Recalibrating...")
            settings.recalibrate()
    # exit the tracker
    elif lower in ["exit", "stop", "quit"]:
        if settings.tracker_active:
            print("You indicated that you wanted to stop...")
            settings.tracker_active = False
    
    # set tracker mode
    if lower in ['eye mode', 'i mode', 'start eye tracker', 'start i tracker']:
        if not settings.tracker_active:
            main.start_tracker('eye')
        else:
            settings.mode = 'eye'
            settings.recalibrate()
    elif lower in ['nose mode', 'snooze mode', 'start nose tracker']:
        if not settings.tracker_active:
            main.start_tracker('nose')
        else:
            settings.mode = 'nose'
            settings.recalibrate()
    
    # part of calibration
    elif lower == "ready":
        settings.said_ready = True

    # mouse control
    if lower == "click" or lower == "quick": 
        g.leftClick()
    elif lower == "right click":
        g.rightClick()
    elif lower == "left click":
        g.leftClick()
    elif lower == "double click":
        g.doubleClick()

    # control the mode (scrolling or mouse movement)
    if lower == "scroll":
        settings.movement_mode = "scroll"
    elif lower == "mouse" or lower == "cursor":
        settings.movement_mode = "cursor"
    
    if lower == "typing on":
        typing_on = True
    elif lower == "typing off":
        typing_on = False

    # application controls
    # open a website
    if lower.startswith("website "):
        webbrowser.open('http://' + lower.split(" ", maxsplit=1)[1].replace(" ", ""))
    # run a program
    elif launcher_on and lower.startswith("open ") or lower.startswith("run ") or lower.startswith("play "):
        _, search = lower.split(" ", maxsplit=1)
        found = start_menu.find_links(search)
        if not found:
            print("No files found!")
        else:
            best_file, _ = found[0]
            print("Opening", best_file, "...")
            if platform.system() == "Windows":
                os.system(f"start \"\" \"{best_file}\"")
    # search google
    elif lower.startswith("google "):
        _, query = lower.split(" ", maxsplit=1)
        webbrowser.open('http://www.google.com/search?q=' + query)

if __name__ == "__main__":
    speech_to_text(typing_on=True, launcher_on=True)
