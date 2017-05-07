import matplotlib
matplotlib.use('TkAgg')

from tkinter import *
from matplotlib.backends.backend_tkagg import *
from matplotlib.backend_bases import key_press_handler

from numpy import arange, sin, pi

class Plotter:

    def __init__(self):
        self.createTk();

    def createTk(self):
        root = Tk.Tk()
        frame = Frame(root);

        # random figure stuff for example
        fig = Figure(figsize=(6,6), dpi = 360)
        add = fig.add_subplot(111)
        t = arange(0.0, 3.0, 0.01)
        sinfunc = sin(2*pi*t)

        add.plot(t, sinfunc)

        #tk.DrawingArea
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.show()
        canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

        toolbar = NavigationToolbar2TkAgg(canvas, root)
        toolbar.update()
        canvas._tkcanvas.pack(side = Tk.TOP, fill=Tk.BOTH, expand = 1)

        def on_key_event(event):
            print("Key pressed")
            key_press_handler(event, canvas, toolbar)

        canvas.mpl_connect('key_press_event', on_key_event)

        def _quit():
            root.quit()
            root.destroy()

        button = Tk.Button(master=root, text='Quit', command=_quit)
        button.pack(side=Tk.BOTTOM)

        Tk.mainloop()


