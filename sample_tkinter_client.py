import Tkinter as tk
import urllib2

root = tk.Tk()

class App(object):
    def __init__(self, master):
        frame = tk.Frame(master)
        frame.pack()

        self.ip = tk.StringVar()
        self.entry = tk.Entry(master, textvariable=self.ip)

        self.open = tk.Button(frame, text="Open",
            command=self.open)
        self.close = tk.Button(frame, text="Close", 
            command=self.close)
        self.entry.pack(side=tk.TOP)
        self.open.pack(side=tk.LEFT)
        self.close.pack(side=tk.LEFT)
    def open(self):
         urllib2.urlopen("http://%s:6000/open_door" % self.ip.get())

    def close(self):
         urllib2.urlopen("http://%s:6000/close_door" % self.ip.get())

app = App(root)

root.mainloop()
