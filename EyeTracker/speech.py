import globals

def speech_to_text():
    import main
    import pyautogui as g
    import speech_recognition as sr
    
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            audio = r.listen(source)
            try:
                text = r.recognize_google_cloud(audio, credentials_json=open("google-credentials.json").read())
            except sr.UnknownValueError:
                print("No text input was supplied")
            else:
                print(f'"{text}"')
                if text == "spacebar":
                    g.press(" ")
                elif "calibrate" in text.lower():
                    print("Recalibrating...")
                    globals.should_calibrate = True
                    globals.has_bottomright = False
                    globals.has_topleft = False
                    globals.msg_bottomright = False
                    globals.msg_topleft = False
                elif text.lower() in ["exit", "stop"]:
                    print("You indicated that you wanted to stop...")
                    globals.should_stop = True
                else:
                    g.typewrite(text)
