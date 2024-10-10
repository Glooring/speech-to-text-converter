# utils.py
import os
import subprocess
from tkinter import messagebox

def show_success_message(file_path):
    """Displays a success message and prompts to open the file location."""
    if messagebox.askyesno("Success", f"Conversion completed successfully.\nThe file is located at:\n{file_path}\n\nDo you want to open the file location?"):
        open_file_location(file_path)

def open_file_location(file_path):
    """Opens the file location in the file explorer."""
    if not os.path.exists(file_path):
        messagebox.showerror("Error", "The path does not exist.")
        return

    if os.name == 'nt':  # For Windows
        normalized_path = os.path.normpath(file_path)
        subprocess.run(['explorer', '/select,', normalized_path], shell=True)
    elif os.name == 'posix':  # For macOS
        subprocess.run(['open', '-R', file_path])
    else:  # Assume Linux
        # Linux file managers may not have a direct way to highlight files.
        directory = os.path.dirname(file_path)
        subprocess.run(['xdg-open', directory])
