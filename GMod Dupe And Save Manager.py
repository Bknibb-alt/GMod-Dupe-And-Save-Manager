import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import time
import signal
import tkinter.messagebox
import tkinter.filedialog
import shutil
from send2trash import send2trash
from PyVDF import PyVDF
import webbrowser
class game():
    def __init__(self, name, path, exepath=None, isunity=False, isunrealengine=False):
        self.name = name
        self.path = path
        self.exepath = exepath
        self.isunity = isunity
        self.isurealengine = isunrealengine
def find_game(name):
    apps = get_games()
    for i in apps:
        if i.name == name:
            return i
def get_games():
    libraryfolders_vdf = PyVDF(infile=os.path.join(os.environ["ProgramFiles(X86)"], "steam/steamapps", "libraryfolders.vdf"))
    libraryfolders = libraryfolders_vdf.getData()
    #print("If You Have Installed A Game And Have Not Restarted Steam Since, Then The Game Will Not Show Up Until Steam Is Restarted!")
    paths = []
    appids = {}
    for i in libraryfolders["libraryfolders"]:
        paths += [libraryfolders["libraryfolders"][i]["path"]]
        appids[libraryfolders["libraryfolders"][i]["path"]] = []
        for k in libraryfolders["libraryfolders"][i]["apps"]:
            appids[libraryfolders["libraryfolders"][i]["path"]] += [k]
    apps = []
    for path in appids:
        appspath = os.path.join(path, "steamapps")
        for appid in appids[path]:
            appmanifestpath = os.path.join(appspath, f"appmanifest_{appid}.acf")
            appmanifest_vdf = PyVDF(infile=appmanifestpath)
            appmanifest = appmanifest_vdf.getData()
            if appmanifest == {}:
                continue
            appname = appmanifest["AppState"]["name"]
            if appname == "Steamworks Common Redistributables":
                continue
            if "installdir" in appmanifest["AppState"]:
                apppath = os.path.join(appspath, "common", appmanifest["AppState"]["installdir"])
            else:
                apppath = os.path.join(appspath, "common", appname)
            isunity = False
            if os.path.isfile(os.path.join(apppath, "UnityPlayer.dll")):
                isunity = True
            elif os.path.isfile(os.path.join(apppath, "UnityCrashHandler64.exe")):
                isunity = True
            elif os.path.isfile(os.path.join(apppath, "UnityCrashHandler32.exe")):
                isunity = True
            isunrealengine = False
            if os.path.isfile(os.path.join(apppath, "Engine/Binaries/Win64/CrashReportClient.exe")):
                isunrealengine = True
            elif os.path.isfile(os.path.join(apppath, "Engine/Binaries/Win64/UnrealCEFSubProcess.exe")):
                isunrealengine = True
            exepath = ""
            if isunity:
                for i in os.listdir(apppath):
                    if os.path.isdir(os.path.join(apppath, i)) and "_Data" in i:
                        if os.path.isfile(os.path.join(apppath, i, "app.info")):
                            exepath = os.path.join(apppath, i[:-5]+".exe")
            elif isunrealengine:
                for root, dirs, files in os.walk(apppath):
                    for file in files:
                        if "-Win64-Shipping.exe" in file:
                            exepath = os.path.join(root, file)
                            break
                    if exepath != "":
                        break
            else:
                for root, dirs, files in os.walk(apppath):
                    if appname+".exe" in files:
                        exepath = os.path.join(root, appname+".exe")
                        break
                    else:
                        if "installdir" in appmanifest["AppState"]:
                            if appmanifest["AppState"]["installdir"]+".exe" in files:
                                exepath = os.path.join(root, appmanifest["AppState"]["installdir"]+".exe")
                                break
            apps += [game(appname, apppath, exepath, isunity, isunrealengine)]
    return apps
gmod = find_game("Garry's Mod")
if gmod is None:
    tkinter.messagebox.showerror("Couldn't Find GMod", "Could Not Find Garry's Mod, You Either Don't Have It Installed Or Need To Restart Steam!")
    raise Exception("Could Not Find Garry's Mod, You Either Don't Have It Installed Or Need To Restart Steam!")
gmod_path = gmod.path
dupes_path = os.path.join(gmod_path, "garrysmod", "dupes")
saves_path = os.path.join(gmod_path, "garrysmod", "saves")
root = tk.Tk()
root.title("Garry's Mod Dupe And Save Manager")
class VerticalScrolledFrame(ttk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame.
    * Construct and pack/place/grid normally.
    * This frame only allows vertical scrolling.
    """
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        self.vscrollbar = ttk.Scrollbar(self, orient="vertical")
        self.vscrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=self.vscrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nesw")
        self.vscrollbar.config(command=self.canvas.yview)

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # Reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.interior = ttk.Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior,
                                           anchor="nw")

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        
        self.interior.bind('<Configure>', self._configure_interior)

        
        self.canvas.bind('<Configure>', self._configure_canvas)
    def _configure_interior(self, event):
        # Update the scrollbars to match the size of the inner frame.
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the canvas's width to fit the inner frame.
            self.canvas.config(width=self.interior.winfo_reqwidth())
    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # Update the inner frame's width to fill the canvas.
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
frame = VerticalScrolledFrame(root)
frame.grid(row=0, column=0, sticky="nesw")
class dupe(ttk.Frame):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.image = Image.open(os.path.join(dupes_path,name+".jpg")).resize((256,256))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.name_label = ttk.Label(self, text=self.name, anchor="center")
        self.name_label.grid(row=0, column=0, sticky="nesw")
        self.image_label = ttk.Label(self, image=self.tk_image, anchor="center")
        self.image_label.grid(row=1, column=0, sticky="nesw")
        self.columnconfigure(0, weight=1)
        self.renaming = False
        self.bind("<Button-3>", self.right_click)
        for i in self.winfo_children():
            i.bind("<Button-3>", self.right_click)
    def right_click(self, event):
        global selected
        selected = self
        do_popup(event)
    def delete(self):
        #os.remove(os.path.join(dupes_path, self.name+".jpg"))
        #os.remove(os.path.join(dupes_path, self.name+".dupe"))
        send2trash([os.path.join(dupes_path, self.name+".jpg").replace(":\\\\", ":\\"),
                    os.path.join(dupes_path, self.name+".dupe").replace(":\\\\", ":\\")])
        refresh()
    def rename(self):
        if self.renaming:
            return
        self.renaming = True
        renamer(self)
    def do_rename(self, rename_name):
        name = rename_name
        count = 1
        while name+".dupe" in os.listdir(dupes_path):
            name = f"{rename_name} ({count})"
            count += 1
        os.rename(os.path.join(dupes_path, self.name+".dupe"), os.path.join(dupes_path, name+".dupe"))
        os.rename(os.path.join(dupes_path, self.name+".jpg"), os.path.join(dupes_path, name+".jpg"))
        self.renaming = False
        refresh()
    def cancel_rename(self):
        self.renaming = False
    def duplicate(self):
        name = self.name
        count = 1
        while name+".dupe" in os.listdir(dupes_path):
            name = f"{self.name} ({count})"
            count += 1
        shutil.copyfile(os.path.join(dupes_path, self.name+".dupe"), os.path.join(dupes_path, name+".dupe"))
        shutil.copyfile(os.path.join(dupes_path, self.name+".jpg"), os.path.join(dupes_path, name+".jpg"))
        refresh()
    def change_image(self):
        extentions = (('Image', '*.png *.jpg *.jpeg *.jpe *.jfif *.heic *.hif *.gif *.tif *.tiff *.bmp *.dib'),
                  ('PNG', '*.png'), ('JPEG', '*.jpg *.jpeg *.jpe *.jfif'), ('HEIC', '*.heic *.hif'), ('GIF', '*.gif'), ('TIFF', '*.tif *.tiff'), ('BITMAP', '*.bmp *.dib'))
        open_file_name = tkinter.filedialog.askopenfilename(title="Open Image", filetypes=extentions)
        image = Image.open(open_file_name)
        if image.size != (512, 512):
            tkinter.messagebox.showinfo("Image Resize", "The Image Will Be Resized To 512x512!")
        image = image.resize((512, 512))
        if tkinter.messagebox.askokcancel("Replace Original", "The Original Image Will Be Replaced, Are You Sure You Want To Replace It?"):
            os.remove(os.path.join(dupes_path, self.name+".jpg"))
            image.save(os.path.join(dupes_path, self.name+".jpg"))
        else:
            return
        refresh()
class save(ttk.Frame):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.image = Image.open(os.path.join(saves_path,name+".jpg")).resize((256,256))
        self.tk_image = ImageTk.PhotoImage(self.image)
        self.name_label = ttk.Label(self, text=self.name, anchor="center")
        self.name_label.grid(row=0, column=0, sticky="nesw")
        self.image_label = ttk.Label(self, image=self.tk_image, anchor="center")
        self.image_label.grid(row=1, column=0, sticky="nesw")
        self.columnconfigure(0, weight=1)
        self.renaming = False
        self.bind("<Button-3>", self.right_click)
        for i in self.winfo_children():
            i.bind("<Button-3>", self.right_click)
    def right_click(self, event):
        global selected
        selected = self
        do_popup(event)
    def delete(self):
        #os.remove(os.path.join(saves_path, self.name+".jpg"))
        #os.remove(os.path.join(saves_path, self.name+".gms"))
        send2trash([os.path.join(saves_path, self.name+".jpg").replace(":\\\\", ":\\"),
                    os.path.join(saves_path, self.name+".gms").replace(":\\\\", ":\\")])
        refresh()
    def rename(self):
        if self.renaming:
            return
        self.renaming = True
        renamer(self)
    def do_rename(self, rename_name):
        name = rename_name
        count = 1
        while name+".gms" in os.listdir(saves_path):
            name = f"{rename_name} ({count})"
            count += 1
        os.rename(os.path.join(saves_path, self.name+".gms"), os.path.join(saves_path, name+".gms"))
        os.rename(os.path.join(saves_path, self.name+".jpg"), os.path.join(saves_path, name+".jpg"))
        self.renaming = False
        refresh()
    def cancel_rename(self):
        self.renaming = False
    def duplicate(self):
        name = self.name
        count = 1
        while name+".gms" in os.listdir(saves_path):
            name = f"{self.name} ({count})"
            count += 1
        shutil.copyfile(os.path.join(saves_path, self.name+".gms"), os.path.join(saves_path, name+".gms"))
        shutil.copyfile(os.path.join(saves_path, self.name+".jpg"), os.path.join(saves_path, name+".jpg"))
        refresh()
    def change_image(self):
        extentions = (('Image', '*.png *.jpg *.jpeg *.jpe *.jfif *.heic *.hif *.gif *.tif *.tiff *.bmp *.dib'),
                  ('PNG', '*.png'), ('JPEG', '*.jpg *.jpeg *.jpe *.jfif'), ('HEIC', '*.heic *.hif'), ('GIF', '*.gif'), ('TIFF', '*.tif *.tiff'), ('BITMAP', '*.bmp *.dib'))
        open_file_name = tkinter.filedialog.askopenfilename(title="Open Image", filetypes=extentions)
        image = Image.open(open_file_name)
        if image.size != (512, 512):
            tkinter.messagebox.showinfo("Image Resize", "The Image Will Be Resized To 512x512!")
        image = image.resize((512, 512))
        if tkinter.messagebox.askokcancel("Replace Original", "The Original Image Will Be Replaced, Are You Sure You Want To Replace It?"):
            os.remove(os.path.join(saves_path, self.name+".jpg"))
            image.save(os.path.join(saves_path, self.name+".jpg"))
        else:
            return
        refresh()
class renamer(tk.Toplevel):
    def __init__(self, object_):
        super().__init__(root)
        self.grab_set()
        self.object = object_
        self.title("Rename Dupe/Save")
        self.name_var = tk.StringVar(master=self, value=self.object.name)
        ttk.Entry(self, width=30, textvariable=self.name_var).grid(row=0, column=0, sticky="nesw")
        ttk.Button(self, text="Rename", command=self.finish).grid(row=1, column=0, sticky="nesw")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.protocol("WM_DELETE_WINDOW", self.cancel)
    def finish(self):
        self.object.do_rename(self.name_var.get())
        self.destroy()
    def cancel(self):
        self.object.cancel_rename()
        self.destroy()
width = 5
last_width = width
selected = None
mode = "Dupes"
modes = ["Dupes", "Saves"]
mode_var = tk.IntVar(value=1)
objects = []
def refresh():
    global width
    global objects
    for i in objects:
        i.destroy()
    objects = []
    x = 0
    y = 0
    if mode == "Dupes":
        for i in os.listdir(dupes_path):
            if os.path.splitext(i)[-1] == ".dupe":
                objects += [dupe("".join(os.path.splitext(i)[:-1]), frame.interior)]
                objects[-1].grid(row=y, column=x, sticky="nesw")
                x += 1
                if x >= width:
                    x = 0
                    y += 1
    elif mode == "Saves":
        for i in os.listdir(saves_path):
            if os.path.splitext(i)[-1] == ".gms":
                objects += [save("".join(os.path.splitext(i)[:-1]), frame.interior)]
                objects[-1].grid(row=y, column=x, sticky="nesw")
                x += 1
                if x >= width:
                    x = 0
                    y += 1
def reconfig_interior(event):
    global width
    width = frame.interior.winfo_width() // 256
    frame._configure_interior(event)
menu = tk.Menu(root, tearoff=0)
mode_menu = tk.Menu(menu, tearoff=0)
menu.add_cascade(label="Mode", menu=mode_menu)
def refresh_mode():
    global mode
    global modes
    global mode_var
    mode = modes[mode_var.get()-1]
    refresh()
count = 1
for i in modes:
    mode_menu.add_radiobutton(label=i, value=count, variable=mode_var, command=refresh_mode)
    count += 1
menu.add_command(label="Please make sure that steam cloud is disabled for GMod!")
menu.add_command(label="Open Github Repository", command=lambda: webbrowser.open("https://github.com/Bknibb-alt/GMod-Dupe-And-Save-Manager"))
root.config(menu=menu)
frame.interior.bind("<Configure>", reconfig_interior)
root.protocol("WM_DELETE_WINDOW", lambda: os.kill(os.getpid(), signal.SIGTERM))
root.geometry("1058x566")
m = tk.Menu(root, tearoff=0)
m.add_command(label="Delete", command=lambda: selected.delete())
m.add_command(label="Rename", command=lambda: selected.rename())
m.add_command(label="Duplicate", command=lambda: selected.duplicate())
m.add_command(label="Change Image", command=lambda: selected.change_image())
m.add_separator()
m.add_command(label="Refresh All", command=refresh)
def on_mousewheel(event):
    frame.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
frame.canvas.bind_all("<MouseWheel>", on_mousewheel)
def do_popup(event):
    try:
        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()
while True:
    if width != last_width:
        last_width = width
        refresh()
    root.update()
