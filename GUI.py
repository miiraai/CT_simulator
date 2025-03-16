import tkinter as tk
from tkinter import ttk, Label
from tkinter import filedialog

from tkinter import *


def browseFiles():
    global img
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select a File",
        filetypes=(("PNG files", "*.png"), ("all files", "*.*"))
    )

    label_file_explorer.configure(text="File Opened: " + filename)

    img = PhotoImage(file=filename)
    image_label.configure(image=img)
    image_label.image = img

def show_values():
    for i in range(0, 180, alpha.get()):
        print("aplha = ", i)
    print (n.get(), l.get())

def openNewWindow():
    global img
    newWindow = Toplevel(root)

    newWindow.title("New Window")

    newWindow.geometry("600x600")

    Label(newWindow,
          text="This is a new window")

    button_exit = Button(newWindow,
                         text="Exit",
                         command=exit)

    button_exit.grid(column=0, row=4)

    if img:
        image_label_new = tk.Label(newWindow, image=img)
        image_label_new.grid(column=0, row=0)

    alpha_value = alpha.get()
    alpha_label = Label(newWindow, text=f"Delta Alpha = {alpha_value}", font=("Arial", 14))
    alpha_label.grid(column=0, row=1)



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
                                width=80, height=4,
                                fg="blue")

    button_explore = Button(root,
                            text="Browse Files",
                            command=browseFiles)

    button_exit = Button(root,
                         text="Exit",
                         command=exit)

    label_file_explorer.grid(column=0, row=2)
    button_explore.grid(column=0, row=3)
    button_exit.grid(column=0, row=4)



    # # In/Out
    # tk.Label(root, text="In/Out").grid(row=0, column=0, sticky=tk.W)
    # direction = ttk.Combobox(root, values=["IN", "OUT"], state="readonly")
    # direction.grid(row=1, column=0, sticky=tk.EW)
    # direction.set("IN")

    nrow = 5

    alpha = Scale(root, from_=1, to=180, orient=HORIZONTAL, label="     delta alpha")
    alpha.grid(column=0, row=nrow)

    n = Scale(root, from_=0, to=180, orient=HORIZONTAL, label="              n")
    n.grid(column=0, row=nrow + 1)

    l = Scale(root, from_=0, to=180, orient=HORIZONTAL, label="              l")
    l.grid(column=0, row=nrow + 2)

    pokaz = tk.Button(root, text="Show", command=show_values)
    pokaz.grid(column=0, row=nrow + 3)

    # zdjecie = PhotoImage(file="scans/Duolingo_Sharing.png")
    #
    # # image_label = tk.Label(root, image=zdjecie)
    # # #image_label = tk.Label(root, image=zdjecie)
    # # image_label.grid(column=0, row=10)

    img = PhotoImage()
    image_label = tk.Label(root, image=img)

    nowe_okno = Button(root,
                            text="Dalej",
                            command=openNewWindow)
    nowe_okno.grid(column=0, row=10)


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

