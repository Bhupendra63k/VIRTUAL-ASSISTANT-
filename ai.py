import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import os
import subprocess
import time
import cv2
import pyautogui
import threading
import pyaudio  # Import pyaudio

# Initialize the text-to-speech engine
engine = pyttsx3.init()

# Set the voice to female
voices = engine.getProperty('voices')
for voice in voices:
    if "female" in voice.name.lower():  # Look for a female voice
        engine.setProperty('voice', voice.id)
        break
else:
    # If no female voice is found, use the first available voice
    engine.setProperty('voice', voices[1].id)

ASSISTANT_NAME = "naru"
CLAP_THRESHOLD = 0.7  # Adjust this value as needed

# Global variable to track assistant state
assistant_sleeping = False

def speak(text):
    """Speak the given text."""
    engine.say(text)
    engine.runAndWait()

def take_picture():
    """Takes a picture using the default camera."""
    try:
        camera = cv2.VideoCapture(0)  # 0 represents the default camera
        if not camera.isOpened():
            speak("Sorry, I can't access the camera.")
            return

        # Allow the camera to warm up
        time.sleep(2)

        ret, frame = camera.read()
        if not ret:
            speak("Sorry, I couldn't capture a picture.")
            camera.release()
            return

        image_name = f"picture_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        cv2.imwrite(image_name, frame)
        camera.release()
        speak(f"Picture saved as {image_name}")

    except Exception as e:
        speak(f"An error occurred while taking the picture: {e}")

def take_screenshot():
    """Takes a screenshot of the current screen."""
    try:
        # Take screenshot
        screenshot = pyautogui.screenshot()

        # Define the filename
        image_name = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        # Save the screenshot
        screenshot.save(image_name)

        speak(f"Screenshot saved as {image_name}")

    except Exception as e:
        speak(f"An error occurred while taking the screenshot: {e}")

def listen():
    """Listen to the user's voice and return the recognized text."""
    recognizer = sr.Recognizer()
    with sr.Microphone(sample_rate=48000) as source:  # Set sample rate
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I didn't understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, there seems to be an issue with the speech recognition service.")
            return None
        except sr.WaitTimeoutError:
            speak("You didn't say anything.")
            return None

def close_bing():
    """Closes the default web browser."""
    try:
        # This command works for Chrome on Windows.  Adjust as needed for other browsers/OS.
        subprocess.call("taskkill /im msedge.exe /f")
        speak("Closing the browser.")
    except:
        speak("I encountered an error trying to close the browser.")

def close_brave():
    """Closes the default web browser."""
    try:
        # This command works for Chrome on Windows.  Adjust as needed for other browsers/OS.
        subprocess.call("taskkill /im brave.exe /f")
        speak("Closing the browser.")
    except:
        speak("I encountered an error trying to close the browser.")

def set_reminder(reminder_text, reminder_time):
    """Sets a reminder that will trigger at the specified time."""
    now = datetime.datetime.now()
    try:
        reminder_time = datetime.datetime.strptime(reminder_time, "%H:%M")
        reminder_time = reminder_time.replace(year=now.year, month=now.month, day=now.day)
    except ValueError:
        speak("Invalid time format. Please use HH:MM format.")
        return

    if reminder_time <= now:
        speak("Reminder time has already passed.")
        return

    time_difference = (reminder_time - now).total_seconds()

    def reminder_function():
        speak(f"Reminder: {reminder_text}")

    timer = threading.Timer(time_difference, reminder_function)
    timer.start()
    speak(f"Reminder set for {reminder_text} at {reminder_time.strftime('%I:%M %p')}")

def perform_task(command):
    """Perform tasks based on the voice command."""
    global assistant_sleeping  # Access the global variable

    if "time" in command:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
    elif "date" in command:
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")
    elif "search on google" in command:
        speak("what should i search for on google and from wikipedia?")
        query = listen()
        if query:
            speak(f"Searching for {query} on Google and Wikipedia")
            webbrowser.open(f"https://www.google.com/search?q={query} wikipedia")

    elif "open deepseek" in command:
        speak("Opening Deepseek")
        webbrowser.open("https://deepseek.com")
    elif "open notepad" in command:
        speak("Opening Notepad")
        os.system("notepad")
    elif "close notepad" in command:
        speak("Closing Notepad")
        os.system("taskkill /im notepad.exe /f")
    elif "open command prompt" in command:
        os.system("start cmd")
    elif "close command prompt" in command:
        os.system("taskkill /im cmd.exe /f")
    elif "open brave" in command:
        speak("Opening Brave Browser")
        os.system("start brave")
    elif "close brave" in command:
        close_brave()
    elif "open bing" in command:
        speak("Opening Bing Browser")
        os.system("start bing")
    elif "close tab" in command:
        close_bing()
    elif "shutdown" in command:
        speak("Shutting down the computer")
        os.system("shutdown /s /t 1")
    elif "restart" in command:
        speak("Restarting the computer")
        os.system("shutdown /r /t 1")
    elif "search on youtube" in command:
        speak("What should I search for on YouTube?")
        query = listen()
        if query:
            speak(f"Searching for {query} on YouTube")
            youtube_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(youtube_url)
            print("Opening YouTube search results...")
        else:
            speak("Sorry, I didn't catch that.")
    elif "open settings" in command:
        speak("Opening Settings")
        os.system("start ms-settings:")
    elif "write a note" in command:
        speak("What should I write?")
        note = listen()
        if note:
            # Open Notepad and write the note
            try:
                subprocess.run(["notepad", "note.txt"], text=True, input=f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {note}\n", check=True)
                speak("Note written successfully in Notepad.")
            except subprocess.CalledProcessError as e:
                speak(f"Error writing note: {e}")
    elif "open vs code" in command:
        speak("Opening Visual Studio Code")
        os.system("code")
    elif "click my pic" in command or "take a picture" in command:
        take_picture()
    elif "open file explorer" in command:
        speak("Opening File Explorer")
        os.system("explorer")
    elif "take a screenshot" in command or "screenshot" in command:
        take_screenshot()
    elif "set a reminder" in command:
        speak("What should I remind you about?")
        reminder_text = listen()
        if reminder_text:
            speak("What time should I remind you? Please use HH:MM format.")
            reminder_time = listen()
            if reminder_time:
                set_reminder(reminder_text, reminder_time)
            else:
                speak("Sorry, I didn't catch the reminder time.")
        else:
            speak("Sorry, I didn't catch the reminder text.")
    elif "open virtualbox" in command:
        speak("Opening VirtualBox")
        os.system("start VirtualBox")
    elif "open copilot" in command:
        speak("Opening GitHub Copilot")
        os.system("start copilot")
    elif "sleep" in command:
        speak("Going to sleep. Clap to wake me up!")
        assistant_sleeping = True
    elif "open whatsapp" in command:
        speak("opening whatsapp")
        os.system("start whatsapp")
    elif "start program" in command:
        speak("Please tell me the name of the program you want to start.")
        program_name = listen()
        if program_name:
            try:
                speak(f"Starting {program_name}")
                os.system(f"start {program_name}")
            except Exception as e:
                speak(f"Sorry, I encountered an error trying to start {program_name}: {e}")
        else:
            speak("Sorry, I didn't catch the program name.")
    elif "bye" in command or "pogo" in command:
        speak("Goodbye!")
        exit()
    else:
        speak("Sorry, I can't perform that task.")

def listen_for_clap():
    """Listens for a clap sound."""
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for clap...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5)
            # Analyze audio for clap sound (this is a simplified approach)
            energy = sum([val**2 for val in audio.get_raw_data()]) / len(audio.get_raw_data())
            if energy > CLAP_THRESHOLD:
                print("Clap detected!")
                return True
            else:
                print("No clap detected.")
                return False
        except sr.WaitTimeoutError:
            print("No sound detected.")
            return False
        except Exception as e:
            print(f"Error listening for clap: {e}")
            return False

def start_assistant():
    """Starts the virtual assistant."""
    global running, assistant_sleeping  # Access the global variables
    running = True
    speak(f"Hello! I am {ASSISTANT_NAME} your virtual assistant. How can I help you?")
    while running:
        if not assistant_sleeping:  # Only listen for commands if not sleeping
            command = listen()
            if command:
                perform_task(command)
        else:
            time.sleep(1)  # Reduce CPU usage while sleeping

def main_loop():
    """Main loop to listen for clap and start the assistant."""
    global assistant_sleeping  # Access the global variable

    while True:
        if assistant_sleeping:
            print("Assistant is sleeping. Listening for clap to wake up...")
            if listen_for_clap():
                assistant_sleeping = False
                speak("I'm awake! How can I help you?")
                start_assistant()
                break  # Exit the loop after waking up
            else:
                time.sleep(1)  # Reduce CPU usage while sleeping
        else:
            if listen_for_clap():
                start_assistant()
                break  # Exit the loop after starting the assistant

if __name__ == "__main__":
    main_loop()