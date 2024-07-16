from playsound import playsound
from gtts import gTTS
import speech_recognition as sr
import os
import time
import datetime
import webbrowser
from configparser import ConfigParser
import google.generativeai as genai

import pathlib
import textwrap
import re
import tkinter as tk
from tkinter import Toplevel, Text, Canvas
import pyttsx3
import speech_recognition as sr
import datetime
import os
import re
from threading import Thread
from PIL import Image, ImageTk, ImageSequence

#* kütüphaneler

#* değiskenler
config = ConfigParser()
r = sr.Recognizer()
ini_var = False

#* settings.ini dosyasını kontrol etmek
dl = os.listdir()
for i in dl:
    if i == "settings.ini":
        ini_var = True

#* settings.ini dosyası varsa yapay zeka ayarlamak
if ini_var:
    config.read('settings.ini')
    api = config['API_KEY']['google_genetive_ai_api']
    genai.configure(api_key=api)
    model_gemini_pro = genai.GenerativeModel('gemini-pro')

#* sesi kaydetmek
def record(ask=False):
    with sr.Microphone() as source:
        if ask:
            pass
        audio = r.listen(source)
        voice = ""
        try:
            voice = r.recognize_google(audio, language="tr-TR")
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            print("sistem hatası")
        return voice

#* konusma
def speak(string):
    # GIF'i göster
    start_gif_animation()
    
    tts = gTTS(text=string, lang="tr", slow=False)
    file = "answer.mp3"
    tts.save(file)
    playsound(file)
    os.remove(file)
    
    # GIF'i durdur
    stop_gif_animation()

#* açılıs sesini oynatma
playsound("acilis.mp3")
if not ini_var:
    speak("Uyarı! settings.ini dosyası bulunamadı veya adı yanlış assistan çalışmaya devam eder ama yapay zeka çalışamaz.")

#* asistan aktiflestirme
def wp(voice):
    if "sistem" in voice or "asistan" in voice or "hey asistan" in voice or "hey" in voice or "system" in voice:
        playsound("giris.mp3")
        speak("efendim")
        voice = record()
        if voice != "":
            voice = voice.lower()
            rp(voice)
            print(voice)
        voice = ""

#* yanıtlar
def rp(voice):
    if "selamın aleyküm" in voice or "selamu naleyküm" in voice:
        speak("Aleyküm selam")
    if "merhaba" in voice:
        speak("merhaba")
    if "nasılsın" in voice:
        speak("iyiyim siz nasılsınız efendim")
    if "sistemi kapat" in voice:
        speak("kapatıyorum")
        time.sleep(1)
        speak("sistem kapandı")
        playsound("cikis.mp3")
        exit()
    if "saat kaç" in voice:
        speak(datetime.datetime.now().strftime("%H:%M"))
    if "google'da ara" in voice:
        speak("ne aratayim?")
        search = record()
        url = "https://www.google.com/search?q={}".format(search)
        webbrowser.get().open(url)
        speak("{} için google'da bulabildiklerimi listeliyorum".format(search))
    if "not et" in voice:
        speak("dosya ismi ne olsun")
        fn = record() + ".txt"
        speak("ne kaydetmek istiyorsun")
        tt = record()
        with open(fn, "w", encoding="utf-8") as f:
            f.writelines(tt)
    if "orman yangınları nedir" in voice:
        speak("Orman yangınları, sadece Türkiye'yi değil, tüm dünyayı etkileyen bir sorundur. Her yıl milyonlarca hektar ormanlık alan yok olmaktadır. Bu durum, küresel ısınmaya ve iklim değişikliğine katkıda bulunmaktadır.Orman yangınları ile mücadele için uluslararası iş birliği şarttır. Ormanların korunması ve yangınların önlenmesi için ortak çalışmalar yapılmalıdır.")
    if "yapay zeka" in voice and ini_var:
        speak("yapay zekada ne aratmak istersiniz")
        promt = record()
        rp = model_gemini_pro.generate_content(promt)
        speak(str(rp.text))
    if "yapay zeka" in voice and not ini_var:
        speak("settings.ini dosyası bulunamadı veya adı yanlış")
    if "komutlar" in voice:
        open_command_window()
    if "takvim etkinliği ekle" in voice:
        add_event(voice)
    if "etkinliklerimi söyle" in voice:
        list_today_events()
    if "yarın ne etkinliklerim var" in voice:
        list_tomorrow_events()

#* ses dinleme
def main():
    while True:
        voice = record()
        if voice != "":
            voice = voice.lower()
            wp(voice)
            print(voice)
            voice = ""
def add_event(voice):
    speak("Etkinlik adını söyleyin.")
    event_name = record()
    speak("Etkinlik ne zaman?")
    event_time = record()

    event_date = datetime.date.today()
    if "bugün" in event_time:
        pass
    elif "yarın" in event_time:
        event_date += datetime.timedelta(days=1)
    else:
        try:
            event_date = datetime.datetime.strptime(event_time, "%d.%m.%Y").date()
        except ValueError:
            speak("Tarihi anlayamadım, lütfen günü ayı ve yılı belirtin (örneğin, 16.05.2024).")
            return

    event_time = re.search(r'\d{1,2}:\d{2}', event_time)
    if event_time:
        event_time = event_time.group()
        event_datetime = datetime.datetime.combine(event_date, datetime.datetime.strptime(event_time, "%H:%M").time())
        speak("Etkinlik {} saat {} olarak {} tarihinde ayarlandı.".format(event_name, event_time, event_date.strftime("%Y-%m-%d %A")))

        with open("events.txt", "a") as f:
            f.write("{} - {}\n".format(event_datetime.strftime("%Y-%m-%d %H:%M"), event_name))
    else:
        speak("Saat bilgisini anlayamadım, lütfen tekrar deneyin.")

def list_today_events():
    today = datetime.date.today()
    with open("events.txt", "r") as f:
        events = f.readlines()
        for event in events:
            event_date_time = event.split(" - ")[0]
            event_date = event_date_time.split(" ")[0]
            if event_date == today.strftime("%Y-%m-%d"):
                speak(event.strip())

def list_tomorrow_events():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    with open("events.txt", "r") as f:
        events = f.readlines()
        for event in events:
            event_date_time = event.split(" - ")[0]
            event_date = event_date_time.split(" ")[0]
            if event_date == tomorrow.strftime("%Y-%m-%d"):
                speak(event.strip())

def remove_past_events():
    current_datetime = datetime.datetime.now()
    with open("events.txt", "r") as f:
        lines = f.readlines()

    with open("events.txt", "w") as f:
        for line in lines:
            event_datetime_str = line.split(" - ")[0]
            event_datetime = datetime.datetime.strptime(event_datetime_str, "%Y-%m-%d %H:%M")
            if event_datetime > current_datetime:
                f.write(line)

def open_command_window():
    command_window = Toplevel(root)
    command_window.title("Komutlar")
    command_window.geometry("300x400")
    command_window.update_idletasks()
    width = command_window.winfo_width()
    height = command_window.winfo_height()
    x = (command_window.winfo_screenwidth() // 2) - (width // 2)
    y = (command_window.winfo_screenheight() // 2) - (height // 2)
    command_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    text_box = Text(command_window, height=20, width=40)
    text_box.pack()
    text_box.insert(tk.END, "Aktifleştirmek İçin\n")
    text_box.insert(tk.END, "↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n")
    text_box.insert(tk.END, "\n")
    text_box.insert(tk.END, "→Sistem\n")
    text_box.insert(tk.END, "→Asistan\n")
    text_box.insert(tk.END, "→hey asistan\n")
    text_box.insert(tk.END, "→hey\n")
    text_box.insert(tk.END, "→system\n")
    text_box.insert(tk.END, "\n")
    text_box.insert(tk.END, "Diğer Komutlar\n")
    text_box.insert(tk.END, "↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓\n")
    text_box.insert(tk.END, "\n")
    text_box.insert(tk.END, "→Selamın Aleyküm\n")
    text_box.insert(tk.END, "→Merhaba\n")
    text_box.insert(tk.END, "→Nasılsın\n")
    text_box.insert(tk.END, "→Sistemi Kapat\n")
    text_box.insert(tk.END, "→Saat Kaç\n")
    text_box.insert(tk.END, "→Google'da Ara\n")
    text_box.insert(tk.END, "→Not Et\n")
    text_box.insert(tk.END, "→Orman Yangınları Nedir\n")
    text_box.insert(tk.END, "→Komutlar\n")
    text_box.insert(tk.END, "→Takvim Etkinliği Ekle\n")
    text_box.insert(tk.END, "→Etkinliklerimi söyle\n")
    text_box.insert(tk.END, "→Yarın Ne Etkinliklerim Var\n")
    text_box.insert(tk.END, "→Yapay Zeka(Şuan Çalışmıyor)\n")

def start_gif_animation():
    global gif_running
    gif_running = True
    animate_gif()

def stop_gif_animation():
    global gif_running
    gif_running = False

def animate_gif():
    global gif_frame_index
    if gif_running:
        gif_frame = gif_frames[gif_frame_index]
        gif_frame_index = (gif_frame_index + 1) % len(gif_frames)
        canvas.itemconfig(gif_image_id, image=gif_frame)
        root.after(100, animate_gif)  # 100 ms delay between frames

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Ana Ekran")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root_width = 800
    root_height = 600
    x_position = (screen_width - root_width) // 2
    y_position = (screen_height - root_height) // 2
    root.geometry(f"{root_width}x{root_height}+{x_position}+{y_position}")

    gif_image = Image.open("sirilike.gif")
    gif_frames = [ImageTk.PhotoImage(frame, master=root) for frame in ImageSequence.Iterator(gif_image)]
    gif_frame_index = 0
    gif_running = False

    canvas = Canvas(root, width=gif_image.width, height=gif_image.height)
    gif_image_id = canvas.create_image(0, 0, anchor=tk.NW, image=gif_frames[0])
    canvas.pack()

    # Global referansları sakla
    canvas.gif_frames = gif_frames

    button = tk.Button(root, text="Komutlar", command=open_command_window,width=15, height=3)
    button.place(relx=1.0, rely=1.0, anchor='se')

    voice_thread = Thread(target=main)
    voice_thread.daemon = True
    voice_thread.start()

    root.mainloop()
    remove_past_events()
    list_today_events()
