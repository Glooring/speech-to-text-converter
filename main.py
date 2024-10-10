import os
import tkinter as tk
from tkinter import filedialog, messagebox
from threading import Thread
import subprocess

from helpers.speech_to_text import SpeechToTextApp
from helpers.utils import show_success_message
# Create a global variable for SpeechToTextApp
speech_app = None
selected_mp3_path = None  # Store selected MP3 path globally

def main():
    global speech_app, selected_mp3_path

    # Create the main window first to ensure the GUI loads instantly
    root = tk.Tk()
    root.title("Speech-to-Text Converter")

    # Center the main window
    window_width, window_height = 400, 180  # Set desired window size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height / 2 - window_height / 2)
    position_right = int(screen_width / 2 - window_width / 2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

    # Title
    title = tk.Label(root, text="Speech-to-Text Converter", font=("Helvetica", 16))
    title.pack(pady=10)

    # MP3 to Text Transcription Section
    def on_transcribe_mp3_to_text():
        global speech_app, selected_mp3_path
        if not speech_app:
            speech_app = SpeechToTextApp()  # Load models in the background

        # Let user select the file immediately
        selected_mp3_path = tk.filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3")])

        if selected_mp3_path:
            # Start a new thread to handle waiting for models and processing transcription
            Thread(target=start_transcription).start()

    # Inside the start_transcription function
    def start_transcription():
        global speech_app, selected_mp3_path
        message_printed = False  # Flag to track if the message has been printed

        # Wait for the models to load
        while not speech_app.models_ready:
            if not message_printed:
                print("Models are still loading, please wait...")
                message_printed = True  # Set the flag to True after printing once
            import time
            time.sleep(2)

        # Once models are loaded, proceed with transcription
        if selected_mp3_path:
            text_file_path = speech_app.transcribe_mp3_to_text(selected_mp3_path)
            if text_file_path:
                show_success_message(text_file_path)
            else:
                messagebox.showerror("Error", "An error occurred during transcription.")


    transcribe_to_text_button = tk.Button(root, text="Choose audio file", command=on_transcribe_mp3_to_text)
    transcribe_to_text_button.pack(pady=10)

    # Close Button
    close_button = tk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=20)

    # Run the main loop of the interface
    root.mainloop()


if __name__ == "__main__":
    main()
