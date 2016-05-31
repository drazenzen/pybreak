#!/usr/bin/env python
# coding: utf-8

import os
import sys
import json
import random
import argparse

try:
    from tkinter import *  # noqa py3
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import messagebox
except ImportError:
    try:
        from Tkinter import *  # noqa py2
        import ttk
        import tkFileDialog as filedialog
        import tkMessageBox as messagebox
    except ImportError as e:
        sys.exit(e)

# TODO pybreak:
# + Nicer handling MainFrame entry_interval value
# + Save configuration file in HOME config directory
# + Add tests


__version__ = '0.1'
__doc__ = """
Relax yourself away from computer.
"""

INTERVAL = 1200  # default (in seconds)


def version():
    """Returns Python, Tkinter and program version."""
    return 'pybreak: {}\nPython: {}\nTkinter: {}'.format(
        __version__, '.'.join(map(str, sys.version_info[:3])), TclVersion)


def debug_info(*args):
    """Prints debug information on console"""
    if DEBUG:
        if args:
            print(args)
        else:
            print(version())


def load_image(img_path):
    """Tries to load PhotoImage from img_path.

    Returns PhotoImage or None on loading failure.
    """
    img = None
    if os.path.exists(img_path):
        try:
            img = PhotoImage(file=img_path)
        except TclError as e:
            msg = "Image format not supported."
            debug_info(msg, e)
    return img


def subsample_image(image, max_width, max_height):
    """
    Subsamples image to a minimal value below max_width and max_height
    arguments, if image width or height are larger than them.
    If they are not than just return the same image.
    """
    w, h = image.width(), image.height()
    debug_info(w, h, max_width, max_height)
    sx = sy = 0
    while w > max_width:
        sx += 1
        w /= 2
    if sx > 0:
        image = image.subsample(sx)
    while h > max_height:
        sy += 1
        h /= 2
    if sy > 0:
        image = image.subsample(sy)
    debug_info(w, h, sx, sy)
    return image


class Config:
    """Load and save program configuration.

    JSON conf file will be saved in same directory as module itself.
    """
    filename = '{}.{}'.format(__file__.split('.')[0], 'json')

    def __init__(self, *args, **kwargs):
        self.data = {}
        self.load()

    def load(self):
        """Load configuration, create it if necessary."""
        if os.path.exists(self.filename):
            with open(self.filename, "rb") as f:
                try:
                    data = f.read().decode()
                    self.data = json.loads(data)
                except ValueError:
                    self.create()
        else:
            self.create()

    def save(self):
        """Save configuration."""
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=4)

    def create(self):
        """Create default configuration."""
        self.data = {}
        self.interval = INTERVAL
        self.data['interval'] = self.interval
        self.data['img_path'] = ""
        self.save()


class MainFrame(ttk.Frame):

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent, padding=(10, 5, 10, 5))
        self.parent = parent
        self.config = Config()
        self.init_str_vars()
        self.init_ui()
        self.running = False
        self.passed = 0
        debug_info(self.config.data)

    def is_int(self, value):
        """Validates integer input."""
        debug_info('interval input={}'.format(value))
        try:
            if value:
                int(value)
        except ValueError:
            return False
        return True

    def init_str_vars(self):
        """Set initial state variables."""
        self.interval = StringVar(value=self.config.data['interval'])
        self.img_path = StringVar(value=self.config.data['img_path'])
        self.text_running = StringVar(value="Run")
        self.text_passed = StringVar(value="00:00")
        self.text_status = StringVar(value="Ready.")

    def init_ui(self):
        """Initialize main frame."""
        self.parent.title("pybreak")
        self.grid(column=0, row=0, sticky=(N, W, E, S))
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)

        # Interval
        ttk.Label(self, text="Interval:", anchor=E).grid(
            column=0, row=0, sticky=(W, E), padx=5, pady=5)
        entry_interval_vcmd = self.register(self.is_int)
        self.entry_interval = ttk.Entry(
            self, textvariable=self.interval, validate='all',
            validatecommand=(entry_interval_vcmd, '%P'))
        self.entry_interval.bind('<FocusOut>', self.on_entry_interval)
        self.entry_interval.grid(column=1, row=0, sticky=(W, E))
        ttk.Label(self, text="in seconds", anchor=W).grid(
            column=2, row=0, sticky=(W, E), padx=5)

        # Image thumbnail
        ttk.Label(self, text="Image:").grid(
            column=0, row=1, sticky=(N, E), padx=5, pady=5)
        self.thumbnail = ttk.Label(self, compound=CENTER)
        self.set_thumbnail()
        self.thumbnail.grid(column=1, row=1, sticky=N, padx=5, pady=5)
        frm_img_btns = ttk.Frame(self)
        ttk.Button(frm_img_btns, text='Choose...',
                   command=self.on_image_select).pack()
        ttk.Button(frm_img_btns, text='Clear',
                   command=self.on_image_clear).pack()
        frm_img_btns.grid(column=2, row=1, sticky=(N, W), padx=5, pady=5)

        # Counter
        self.label_time = ttk.Label(
            self, textvariable=self.text_passed, font="-weight bold")
        self.label_time.grid(column=0, row=2, sticky=E)

        # Controls
        frm_btns = ttk.Frame(self)
        self.btn_run = ttk.Button(frm_btns, textvariable=self.text_running)
        self.btn_run.pack(side=LEFT, expand=True, fill=X)
        self.btn_run.bind("<1>", self.on_run)
        ttk.Button(frm_btns, text="Preview", command=self.on_preview).pack(
            side=LEFT, expand=True, fill=X)
        ttk.Button(frm_btns, text="Info", command=self.on_info).pack(
            side=LEFT, expand=True, fill=X)
        ttk.Button(frm_btns, text="Quit", command=self.on_quit).pack(
            side=LEFT, expand=True, fill=X)
        frm_btns.grid(column=0, row=8, columnspan=3, sticky=(E, W), ipady=5)

        # Status bar
        self.status = ttk.Label(self, textvariable=self.text_status, anchor=W)
        self.status.grid(column=0, row=9, columnspan=3, sticky=W)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

    def on_entry_interval(self, event):
        """Checks and sets interval value."""
        try:
            value = int(self.interval.get())
        except ValueError:
            value = INTERVAL
        self.interval.set(value)
        self.config.data['interval'] = value

    def on_save(self):
        """Save program configuration."""
        try:
            interval = int(self.interval.get())
        except ValueError as e:
            debug_info(e)
            interval = INTERVAL
        self.config.data['interval'] = interval
        self.config.data['img_path'] = self.img_path.get()
        self.config.save()
        self.interval.set(interval)

    def on_run(self, event):
        """Starts or stops work loop."""
        self.running = not self.running
        if self.running:
            self.text_running.set("Stop")
            self.text_status.set("Running...")
            self.run()
        else:
            self.stop()

    def run(self):
        """Work loop.

        Runs every second, shows RelaxFrame if work is done."""
        if self.running:
            if self.passed >= self.config.data['interval']:
                self.stop()
                RelaxFrame(self, self.img_path.get())
                self.hide()
            else:
                self.passed += 1
                self.parent.after(1000, self.run)
        self.text_passed.set("{}:{}".format(
            str(int(self.passed / 60)).zfill(2),
            str(self.passed % 60).zfill(2)))

    def stop(self):
        """Reset work loop."""
        self.passed = 0
        self.running = False
        self.text_running.set("Run")
        self.text_status.set("Ready.")

    def on_image_select(self):
        """Opens file dialog to select relaxing image."""
        options = {}
        if self.img_path.get():
            options['initialdir'] = os.path.dirname(self.img_path.get())
        else:
            options['initialdir'] = os.path.expanduser("~")
        options['defaultextension'] = ".png"
        options['filetypes'] = [
            ('PNG', '*.png'), ('GIF', '*.gif'), ('All files', '.*')]
        options['parent'] = self.parent
        options['title'] = 'Choose a relax image...'
        filename = filedialog.askopenfilename(**options)
        if filename:
            self.img_path.set(filename)
            if not self.set_thumbnail():
                self.text_status.set("Image format not supported.")
            else:
                self.text_status.set("Image loaded.")

    def set_thumbnail(self):
        """Tries to load image and set image thumbnail."""
        img = load_image(self.img_path.get())
        if img:
            img = subsample_image(img, 160, 160)
            self.thumbnail.config(text='')
            self.thumbnail.config(image=img)
            self.thumbnail.img = img
            return True
        else:
            self.thumbnail.config(image='')
            self.thumbnail.config(text="Default relax frame")
            self.thumbnail.img = None
            return False

    def on_image_clear(self):
        self.img_path.set("")
        self.thumbnail.config(image='')
        self.thumbnail.config(text="Default relax frame")
        self.thumbnail.img = None
        self.text_status.set("Image cleared. Using default Relax frame.")

    def on_preview(self):
        """Preview (test) RelaxFrame."""
        RelaxFrame(self, self.img_path.get())

    def hide(self):
        """Hides itself when work loop starts."""
        self.parent.withdraw()

    def show(self):
        """Shows itself."""
        self.parent.update()
        self.parent.deiconify()

    def on_info(self):
        """Shows program info."""
        prg_detail = "Relax yourself away from computer.\n"
        img_detail = "Supported image formats: {}\n"
        if TkVersion >= 8.5:
            formats = "PNG, GIF"
        else:
            formats = "GIF"
        img_detail = img_detail.format(formats)
        tech_detail = version()
        detail = '\n'.join([prg_detail, img_detail, tech_detail])
        messagebox.showinfo(
            'About', 'pybreak',
            detail=detail)

    def on_quit(self):
        """Saves configuration and exists program."""
        self.on_save()
        self.quit()


class RelaxFrame(Toplevel):
    """Relax frame."""

    def __init__(self, caller, img_path):
        """Give frame a focus and put it on top of all other windows.

        Hides caller frame.
        """
        self.caller = caller
        self.img_path = img_path
        self.img = None
        Toplevel.__init__(self)
        self.init_ui()
        self.focus()
        self.focus_set()
        self.lift()
        self.attributes('-topmost', True)
        self.attributes('-topmost', False)
        self.caller.hide()

    def init_ui(self):
        """Tries to load an image, else shows randomized ellipses."""
        self.config(bg="black")
        self.w, self.h = 640, 480
        self.c = Canvas(self, bg="black", height=self.h, width=self.w)
        self.font = '-*-fixed-medium-*-normal-*-9-*-*-*-*-*-*-*'
        self.colors = [
            'dark sea green', 'sea green', 'medium sea green',
            'light sea green', 'pale green', 'spring green', 'lawn green',
            'medium spring green', 'green yellow', 'lime green',
            'yellow green', 'forest green', 'olive drab', 'dark khaki',
            'khaki', 'pale goldenrod', 'light goldenrod yellow'
        ]
        self.img = load_image(self.img_path)
        if self.img:
            self.img = subsample_image(self.img, self.w, self.h)
            self.c.create_image(0, 0, anchor=NW, image=self.img)
            self.w, self.h = self.img.width(), self.img.height()
            self.c.config(width=self.w, height=self.h)
        else:
            self.ellipses()
        self.c.create_text(
            self.w - 80, self.h - 20, anchor=SW,
            font=self.font, text="ESC to exit...", fill="green")
        self.c.pack()
        self.bind('<Escape>', self.on_close)
        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def on_close(self, *args):
        """Calls caller show method and close itself."""
        self.caller.show()
        self.destroy()

    def ellipses(self):
        """Draws grid, text message and random ellipses on canvas."""
        # grid
        for i in range(0, 640, 40):
            # x lines
            self.c.create_line(0, i, 640, i, fill="gray10")
            self.c.create_text(
                2, i, text=str(i), fill="gray30", anchor=SW, font=self.font)
            # y lines
            self.c.create_line(i, 0, i, 480, fill="gray10")
            self.c.create_text(
                i + 2, 12, text=str(i), fill="gray30", anchor=SW, font=self.font)
        # random ellipses
        offset = 60
        for i in range(1, 10):
            x1 = random.randint(offset, self.w - offset)
            y1 = random.randint(offset, self.h - offset)
            x2 = random.randint(offset, self.w - offset)
            y2 = random.randint(offset, self.h - offset)
            color = "{}".format(
                self.colors[random.randint(0, len(self.colors) - 1)])
            self.c.create_oval(x1, y1, x2, y2, fill=color, outline="")
        # text
        self.c.create_text(
            60, 80, anchor=W, text="Relax for a bit or two...", fill="white")


def gui():
    """Creates main root Tk window and starts mainloop."""
    root = Tk()
    root.resizable(False, False)
    if os.path.exists('images'):  # taskbar/window list images
        if os.name == 'nt':
            root.wm_iconbitmap(
                default=os.path.join(os.getcwd(), 'images/pybreak.ico'))
            # Windows hack to show icon in task bar
            import ctypes
            appid = 'k2.util.pybreak.0.1'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)
        elif TkVersion >= 8.5:
            file = 'pybreak.png' if TkVersion >= 8.6 else 'pybreak.gif'
            icons = [PhotoImage(file=os.path.join(os.getcwd(), 'images', file))]
            root.tk.call('wm', 'iconphoto', str(root), "-default", *icons)
    MainFrame(root)
    root.mainloop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Relax yourself away from computer.")
    parser.add_argument(
        "-v", "--version", action="store_true",
        help="prints program, Python and Tkinter versions")
    parser.add_argument(
        "-d", "--debug", action="store_true",
        help="prints debug information on console")
    args = parser.parse_args()
    DEBUG = args.debug
    if args.version:
        print(version())
    else:
        debug_info()
        gui()
