import tkinter as tk
from tkinter import ttk, Label
from tkinter import filedialog

from tkinter import *


def browseFiles():
    filename = tk.filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("Text files",  "*.txt*"), ("all files", "*.*")))

    label_file_explorer.configure(text="File Opened: "+filename)


if __name__ == "__main__":
    # inicjalizacja glownego okna GUI
    root = tk.Tk()
    root.title("CT Simulator")

    frame = tk.Frame(root, padx=10, pady=10)
    frame.grid(row=0, column=0)

    # lista pol wystepujacych w oknie
    fields = [
        "In/Out", "alpha", "liczba detektorow n", "rozpieosc ukladu l",
    ]
    entries = []

    # Create a File Explorer label
    label_file_explorer = Label(root,
                                text="File Explorer using Tkinter",
                                width=100, height=4,
                                fg="blue")

    button_explore = Button(root,
                            text="Browse Files",
                            command=browseFiles)

    button_exit = Button(root,
                         text="Exit",
                         command=exit)

    label_file_explorer.grid(column=1, row=1)

    button_explore.grid(column=1, row=2)

    button_exit.grid(column=1, row=3)

    # In/Out
    tk.Label(frame, text="In/Out").grid(row=0, column=0, sticky=tk.W)
    direction = ttk.Combobox(frame, values=["IN", "OUT"], state="readonly")
    direction.grid(row=0, column=1, sticky=tk.EW)
    direction.set("IN")
    #
    # # IP Ports
    # for i, field in enumerate(fields[1:-2], start=1):
    #     tk.Label(frame, text=field).grid(row=i, column=0, sticky=tk.W)
    #     entry = tk.Entry(frame)
    #     entry.grid(row=i, column=1, sticky=tk.EW)
    #     entries.append(entry)
    #
    # # Protocol
    # tk.Label(frame, text="Protocol").grid(row=7, column=0, sticky=tk.W)
    # protocol = ttk.Combobox(frame, values=["ALL", "TCP", "UDP", "ICMP"], state="readonly")
    # protocol.grid(row=7, column=1, sticky=tk.EW)
    # protocol.set("ALL")
    #
    # # Action
    # tk.Label(frame, text="Action").grid(row=8, column=0, sticky=tk.W)
    # action = ttk.Combobox(frame, values=["ALLOW", "BLOCK"], state="readonly")
    # action.grid(row=8, column=1, sticky=tk.EW)
    # action.set("ALLOW")

    root.mainloop()

