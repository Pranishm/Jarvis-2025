# ============================
# feature.py
# Jarvis Assistant Core Logic
# Uses Gemini 1.5 Flash + Porcupine Hotword
# ============================

import os
import struct
import subprocess
import time
import webbrowser
import sqlite3

import eel
import pvporcupine
import pyaudio
import pyautogui
import pywhatkit as kit
import pygame
from shlex import quote

# Gemini & HugChat
import google.generativeai as genai
from hugchat import hugchat

# Local modules
from backend.command import speak
from backend.config import ASSISTANT_NAME
from backend.helper import extract_yt_term, remove_words

# DB connection
conn = sqlite3.connect("jarvis.db")
cursor = conn.cursor()

# Init Pygame for sound
pygame.mixer.init()

# ✅ Setup Gemini (HARD CODED)
genai.configure(api_key="AIzaSyAPfoNoe6C5mmEe41tSPssmEhqqQgFBIfA")
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

@eel.expose
def play_assistant_sound():
    """ Play startup sound """
    sound_file = r"C:\Users\nithy\Jarvis-2025\frontend\assets\audio\start_sound.mp3"
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play()


def openCommand(query):
    """ Open apps or websites """
    query = query.replace(ASSISTANT_NAME, "").replace("open", "").strip().lower()

    if not query:
        return

    try:
        cursor.execute('SELECT path FROM sys_command WHERE name=?', (query,))
        result = cursor.fetchone()

        if result:
            speak(f"Opening {query}")
            os.startfile(result[0])
        else:
            cursor.execute('SELECT url FROM web_command WHERE name=?', (query,))
            result = cursor.fetchone()

            if result:
                speak(f"Opening {query}")
                webbrowser.open(result[0])
            else:
                speak(f"Opening {query}")
                os.system(f'start {query}')
    except Exception as e:
        print(f"Error: {e}")
        speak("Something went wrong while opening.")


def PlayYoutube(query):
    """ Play video on YouTube """
    search_term = extract_yt_term(query)
    speak(f"Playing {search_term} on YouTube")
    kit.playonyt(search_term)


def hotword():
    """ Hotword listener using Porcupine """
    porcupine = None
    paud = None
    audio_stream = None

    try:
        porcupine = pvporcupine.create(
            access_key="ZqyXFUDu+FOwur4ohtF6n467yZ2hIrzx1+ow86pkgLXGIgAdEzLc6A==",
            keywords=["jarvis", "alexa"]
        )
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length,
        )

        print("Listening for hotword...")
        while True:
            keyword = audio_stream.read(porcupine.frame_length)
            keyword = struct.unpack_from("h" * porcupine.frame_length, keyword)
            keyword_index = porcupine.process(keyword)

            if keyword_index >= 0:
                print("Hotword detected!")
                pyautogui.keyDown("win")
                pyautogui.press("j")
                time.sleep(2)
                pyautogui.keyUp("win")

    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Hotword error: {e}")
    finally:
        if porcupine:
            porcupine.delete()
        if audio_stream:
            audio_stream.close()
        if paud:
            paud.terminate()


def findContact(query):
    """ Find phone number in contacts """
    query = remove_words(query, [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']).strip().lower()

    try:
        cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ?", ('%' + query + '%',))
        result = cursor.fetchone()

        if result:
            mobile_number = result[0]
            if not str(mobile_number).startswith('+91'):
                mobile_number = '+91' + str(mobile_number)
            return mobile_number, query
        else:
            speak("Contact not found.")
            return None, None

    except Exception as e:
        print(f"Contact error: {e}")
        speak("Error looking up contact.")
        return None, None


def whatsApp(Phone, message, flag, name):
    """ Send WhatsApp message or call """
    if flag == 'message':
        target_tab = 12
        jarvis_message = f"Message sent successfully to {name}"
    elif flag == 'call':
        target_tab = 7
        message = ''
        jarvis_message = f"Calling {name}"
    else:
        target_tab = 6
        message = ''
        jarvis_message = f"Starting video call with {name}"

    encoded_message = quote(message)
    whatsapp_url = f"whatsapp://send?phone={Phone}&text={encoded_message}"
    subprocess.run(f'start "" "{whatsapp_url}"', shell=True)
    time.sleep(5)

    pyautogui.hotkey('ctrl', 'f')
    for _ in range(target_tab):
        pyautogui.hotkey('tab')

    pyautogui.hotkey('enter')
    speak(jarvis_message)


@eel.expose
def chatBot(query):
    """ Talk with Gemini, fallback to HugChat """
    user_input = query.strip()
    response_text = ""

    try:
        response = gemini_model.generate_content(user_input)
        response_text = response.text
    except Exception as gemini_error:
        print(f"Gemini error: {gemini_error}")
        try:
            chatbot = hugchat.ChatBot(cookie_path="backend/cookie.json")
            id = chatbot.new_conversation()
            chatbot.change_conversation(id)
            response_text = chatbot.chat(user_input)
        except Exception as hug_error:
            print(f"HugChat fallback failed: {hug_error}")
            response_text = "Sorry, I could not process your request."

    print(response_text)
    speak(response_text)
    return response_text
