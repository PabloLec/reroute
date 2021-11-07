import tkinter as tk
import gebco
from multiprocessing import Process, Value
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from time import sleep
import time
from pathlib import Path

exit_messages = {
    0: "Fichier KML enregistré sous ",
    1: "Pas de route optimisée trouvée",
}


def start_search(*args, **kwargs):
    A = (entry_A_LONG.get(), entry_A_LAT.get())
    B = (entry_B_LONG.get(), entry_B_LAT.get())
    dist = entry_dist.get()

    sensor = list.curselection()[0]
    file_name = time.strftime("reroute-%Y%m%d-%H%M%S.kml")
    save_path = Path(folder_path.get()) / file_name

    exit_code = Value("i", 0, lock=False)

    p = Process(
        target=gebco.main,
        args=(A, B, dist, sensor, save_path, exit_code),
    )
    p.start()
    p.join()

    message = exit_messages[exit_code.value]
    if exit_code.value == 0:
        message += str(save_path)

    messagebox.showinfo(message=message)


root = tk.Tk()
root.title("reroute 0.0.1")
tk.Label(root, text="     \n   ").grid(row=0)
point_A = tk.Label(text="Point de départ")
point_A.grid(row=1, columnspan=2)
tk.Label(text="Latitude").grid(row=2)
entry_A_LAT = tk.Entry(fg="white", bg="black", width=50)
entry_A_LAT.grid(row=2, column=1)
tk.Label(text="Longitude").grid(row=3)
entry_A_LONG = tk.Entry(fg="white", bg="black", width=50)
entry_A_LONG.grid(row=3, column=1)
tk.Label(root, text="     \n   ").grid(row=4)


point_B = tk.Label(text="Point d'arrivée")
point_B.grid(row=5, columnspan=2)
tk.Label(text="Latitude").grid(row=6)
entry_B_LAT = tk.Entry(fg="white", bg="black", width=50)
entry_B_LAT.grid(row=6, column=1)
tk.Label(text="Longitude").grid(row=7)
entry_B_LONG = tk.Entry(fg="white", bg="black", width=50)
entry_B_LONG.grid(row=7, column=1)
tk.Label(root, text="     \n   ").grid(row=8)

distance = tk.Label(text="Distance")
distance.grid(row=9)
entry_dist = tk.Entry(fg="white", bg="black", width=50)
entry_dist.grid(row=9, column=1)

tk.Label(root, text="     \n   ").grid(row=10)

point_A = tk.Label(text="Type de senseur")
point_A.grid(row=10, columnspan=2)
list = tk.Listbox(root, selectmode="browse", height=4, width=50)
list.grid(row=11, columnspan=2)

x = ["Tout petit fond", "Petit fond", "Moyen fond", "Grand fond"]

for each_item in range(len(x)):

    list.insert(tk.END, x[each_item])

    # coloring alternative lines of listbox
    list.itemconfig(each_item, bg="grey" if each_item % 2 == 0 else "black")


def browse_button():
    global folder_path
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    print(filename)


tk.Label(root, text="     \n   ").grid(row=14)
folder_path = tk.StringVar()
folder = tk.Label(text="Dossier de sauvegarde")
folder.grid(row=15)
browse = tk.Button(text="Sélectionner", command=browse_button)
browse.grid(row=15, column=1)

tk.Label(root, text="     \n   ").grid(row=16)
button = tk.Button(
    text="Valider",
    width=50,
    height=2,
    bg="blue",
    fg="yellow",
)
button.bind("<Button-1>", start_search)
button.grid(row=17, columnspan=2)

root.mainloop()
