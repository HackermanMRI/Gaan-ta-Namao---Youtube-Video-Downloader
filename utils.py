import tkinter as tk
from tkinter import messagebox

def show_message(title, message):
    """
    Displays a message box to the user.
    :param title: The title of the message box.
    :param message: The message to display.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo(title, message)
    root.destroy()
