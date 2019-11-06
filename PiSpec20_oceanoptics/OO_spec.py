import seabreeze.spectrometers as sb

import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
style.use("ggplot")

from sys import version_info
if version_info.major == 2:
    # use Python 2.7 style
    import Tkinter as tk
    import ttk
elif version_info.major == 3:
    # use Python 3.x style
    import tkinter as tk
    from tkinter import ttk

LARGE_FONT= ("Verdana", 12)
NORM_FONT= ("Verdana", 10)

# Enumerate spectrometer, set a default integration, get x & y extents
spec = sb.Spectrometer.from_serial_number()
IntTime = 20000  #20 ms, set default integration time to a reasonable value
spec.integration_time_micros(IntTime)
x = spec.wavelengths()
data = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
xmin = np.around(min(x), decimals=2)
xmax = np.around(max(x), decimals=2)
ymin = np.around(min(data), decimals=2)
ymax = np.around(max(data), decimals=2)
minIntTime =spec.minimum_integration_time_micros

def popupmsg(msg):  # in case you want to have warning popup
    popup = tk.Tk()
    popup.wm_title("!")
    popup.geometry('300x200-100+200')
    label = ttk.Label(popup, text=msg, font=NORM_FONT, wraplength = 250)
    label.pack(side="top", fill="x", pady=10)
    B1 = ttk.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()

class Spec(tk.Tk):
    def __init__(self, ax, *args, **kwargs):
        global data, x, dark, incident
        global IntTime, Averages
        global xmin, xmax, ymin, ymax
        global AbMode
        global monitorwave, monitorindex, monitor

        x = spec.wavelengths()
        # Integration time set above
        Averages=1   #set default averages to a reasonable value
        dark = np.zeros(len(x))
        incident = np.ones(len(x))  #dummy values to prevent error in Absorbance when no dark recorded
        AbMode = 0      #start in raw intensity mode
        
        self.ax = ax
        self.x = x
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin 
        self.ymax = ymax
        self.data = data
        self.line = Line2D(self.x, self.data, color='red')
        self.ax.add_line(self.line)
        self.ax.set_ylim(ymin*0.8, ymax*1.1)
        self.ax.set_xlim(self.xmin, self.xmax)
        monitorwave = np.median(x)  #set monitor wavelength to middle of hardware range

        tk.Tk.__init__(self, *args, **kwargs)
        # tk.Tk.iconbitmap(self, default="clienticon.ico")  set window icon
        tk.Tk.wm_title(self, "Ocean Optics Spectrometer Control")
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        label = tk.Label(self, text="Spectrometer on a Pi", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        self.frame1 = tk.Frame(self)
        self.frame1.pack(side='left', anchor=tk.N)
        labelint = tk.Label(self.frame1, text='Integration Time (ms)', relief='ridge')    
        labelint.pack(side='top', pady=2)
        labelavg = tk.Label(self.frame1, text='# of spectra to average', relief='ridge', width='17', wraplength='100')
        labelavg.pack(side='top', pady=1)
        labelxmin = tk.Label(self.frame1, text='Minimum wavelength', relief='ridge')
        labelxmin.pack(side='top', pady=2)
        labelxmax = tk.Label(self.frame1, text='Maximum wavelength', relief='ridge')
        labelxmax.pack(side='top', pady=2)
        self.button_dark = tk.Button(self.frame1, text='Measure Dark', background='light grey')
        self.button_dark.pack(side='top', pady=2)
        self.button_dark.bind('<ButtonRelease-1>', self.getdark)
        self.buttonAbMode = tk.Button(self.frame1, text='Absorbance Mode (off)', background = 'light grey')
        self.buttonAbMode.pack(side='top', pady=1)
        self.buttonAbMode.bind('<ButtonRelease-1>', self.AbMode)

        monitorindex = np.searchsorted(x, monitorwave, side='left')
        monitor = np.round(self.data[monitorindex], decimals=3)
        self.text = self.ax.text(0.9, 0.9, monitor, transform=ax.transAxes, fontsize=14)
        self.ax.axvline(x=monitorwave, lw=2, color='blue', alpha  = 0.5)
        
        self.labelmonitor = tk.Label(self.frame1, text='Wavelength to monitor (nm)', font=LARGE_FONT)
        self.labelmonitor.pack(side='top')
        self.entrymonitor = tk.Entry(self.frame1, width='7')
        self.entrymonitor.pack(side='top', pady=1, anchor=tk.N)
        self.entrymonitor.insert(0, np.round(x[monitorindex], decimals=2))
        self.entrymonitor.bind('<Return>', self.entrymonitor_return)
        self.labelmonitor2 = tk.Label(self.frame1, text="press <Enter> to set new wavelength")
        self.labelmonitor2.pack(side='top')
        self.button_reset_y = tk.Button(self.frame1, text='Reset Y axis scale', background='light blue')
        self.button_reset_y.pack(side='top', pady=10)
        self.button_reset_y.bind('<ButtonRelease-1>', self.reset_y)
        
        self.frame2 = tk.Frame(self)
        self.frame2.pack(side='left', anchor=tk.N)
        self.entryint = tk.Entry(self.frame2, width='6')
        self.entryint.pack(side='top', pady=1, anchor=tk.N)
        self.entryint.insert(0, IntTime/1000)
        self.entryint.bind('<Return>', self.EntryInt_return)
        self.entryavg = tk.Entry(self.frame2, width='4')
        self.entryavg.pack(side='top', pady=5)
        self.entryavg.insert(0, Averages)
        self.entryavg.bind('<Return>', self.EntryAvg_return)
        self.entryxmin = tk.Entry(self.frame2, width='7')
        self.entryxmin.pack(side='top', pady=2)
        self.entryxmin.insert(0, xmin)
        self.entryxmin.bind('<Return>', self.Entryxmin_return)
        self.entryxmax = tk.Entry(self.frame2, width='7')
        self.entryxmax.pack(side='top', pady=2)
        self.entryxmax.insert(0, xmax)
        self.entryxmax.bind('<Return>', self.Entryxmax_return)
        self.button_incident = tk.Button(self.frame2, text='Measure 100% T', background='light grey') 
        self.button_incident.pack(side='top', pady=2)
        self.button_incident.bind('<ButtonRelease-1>', self.getincident)
        
        button_quit = ttk.Button(self, text='Quit')
        button_quit.pack(side='right', anchor=tk.N)
        button_quit.bind('<ButtonRelease-1>', self.ButtonQuit)

        ax.set_xlabel('Wavelength (nm)')
        ax.set_ylabel('Counts')

        canvas = FigureCanvasTkAgg(fig, self)
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def update(self, data):
        global AbMode
        self.data = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)

        if AbMode==1:
            self.data = np.array(self.data, dtype=float)
            self.data = np.log10((incident-dark)/(self.data-dark))
            self.line.set_data(self.x, self.data)
            monitor = np.round(self.data[monitorindex], decimals=3)
            self.text.set_text(monitor)
            return self.line,

        else:
            #y-axis handled by reset button 
            self.line.set_data(self.x, self.data)
            monitor = np.round(self.data[monitorindex], decimals=3)
            self.text.set_text(monitor)        
            return self.line,
    
    def ButtonQuit(root, event):
            root.destroy()
            exit()

    def getdark(self, event):
        global dark
        darkj = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
        dark = np.array(darkj, dtype=float)
        self.button_dark.configure(background = 'light green')
        
    def getincident(self,event):
        global incident
        incidentj = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
        incident = np.array(incidentj, dtype=float)
        self.button_incident.configure(background = 'light green')
        
        # SET CONFIGURATION
    def setconfig(self):
        global IntTime
        spec.integration_time_micros(IntTime)
        # write new configuration to dialog        
        self.entryint.delete(0, "end")
        self.entryint.insert(0,IntTime / 1000)  #write ms, but IntTime is microseconds
        self.entryavg.delete(0, "end")
        self.entryavg.insert(0,Averages)  #set text in averages box

    def EntryInt_return(self, event):
        global IntTime
        #typically OO spectrometers cant read faster than 4 ms
        IntTimeTemp = self.entryint.get()
        if IntTimeTemp.isdigit() == True:
            if int(IntTimeTemp) > 65000:
                msg = "The integration time must be 65000 ms or smaller.  You set " +(IntTimeTemp)
                self.setconfig()
                popupmsg(msg)
            elif int(IntTimeTemp) < 4:
                msg = "The integration time must be greater than 4 ms.  You set " +(IntTimeTemp)
                self.setconfig()
                popupmsg(msg)
            else:
                IntTime = int(IntTimeTemp) * 1000  #convert ms to microseconds
                self.setconfig()
        else:
            msg = "Integration time must be an integer between 4 and 65000 ms.  You set " +str(IntTimeTemp)
            self.setconfig()
            popupmsg(msg)

    def EntryAvg_return(self, event):
        ## averaging needs to be implemented here in code
        #  cseabreeze has average working, but python-seabreeze doesn't (2019)
        global Averages
        Averages = self.entryavg.get()
        if Averages.isdigit() == True:
            Averages = int(float(Averages))
        else:
            msg = "Averages must be an integer.  You tried " + str(Averages) + ".  Setting value to 1."
            Averages = 1
            self.entryavg.delete(0, "end")
            self.entryavg.insert(0,Averages)  #set text in averages box
            popupmsg(msg)

    def Entryxmax_return(self,event):
        global xmax
        xmaxtemp = self.entryxmax.get()
        try:
            float(xmaxtemp)
            xmaxtemp = float(self.entryxmax.get())
            if xmaxtemp > xmin:
                xmax = xmaxtemp
                self.entryxmax.delete(0, 'end')
                self.entryxmax.insert(0, xmax)  #set text in box
                self.ax.set_xlim(xmin,xmax)
            else:
                msg = "Maximum wavelength must be larger than minimum wavelength.  You entered " + str(xmaxtemp) + " nm."
                self.entryxmax.delete(0, 'end')
                self.entryxmax.insert(0, xmax)  #set text in box
                popupmsg(msg)
        except:
            self.entryxmax.delete(0, 'end')
            self.entryxmax.insert(0, xmax)  #set text in box to unchanged value

    def Entryxmin_return(self, event):
        global xmin
        xmintemp = self.entryxmin.get()
        try:
            float(xmintemp)
            xmintemp = float(self.entryxmin.get())
            if xmintemp < xmax:
                xmin = xmintemp
                self.entryxmin.delete(0, 'end')
                self.entryxmin.insert(0, xmin)  #set text in box
                self.ax.set_xlim(xmin,xmax)
            else:
                msg = "Minimum wavelength must be smaller than maximum wavelength.  You entered " + str(xmintemp) + " nm."
                self.entryxmin.delete(0, 'end')
                self.entryxmin.insert(0, xmin)  #set text in box
                popupmsg(msg)
        except:
            self.entryxmin.delete(0, 'end')
            self.entryxmin.insert(0, xmin)  #set text in box to unchanged value

    def AbMode(self, event):
        global AbMode
        if AbMode == 1:
            AbMode = 0
            ax.set_ylabel('Counts')
            self.buttonAbMode.configure(text='Absorbance Mode (off)', background = 'light grey')
            self.reset_y(self)
        else:
            AbMode = 1
            ax.set_ylabel('Absorbance')
            ax.set_ylim(-0.1,1.2)
            self.buttonAbMode.configure(text='Absorbance Mode (on)', background = 'light green')


    def reset_y(self, event):
        if AbMode == 0:
            data = spec.intensities(correct_dark_counts=True, correct_nonlinearity=True)
            ymin = min(data)
            ymax = max(data)
            ax.set_ylim(ymin * 0.9, ymax * 1.1)
        else:
            pass

    def entrymonitor_return(self, event):
        global monitorwave, monitorindex, x
        monitorwavetemp = self.entrymonitor.get()
        try:
            float(monitorwavetemp)
            monitorwavetemp = float(self.entrymonitor.get())
            if xmin < monitorwavetemp < xmax:
                monitorwave = monitorwavetemp                
                monitorindex = np.searchsorted(x, monitorwave, side='left')
                monitorwave = np.around(x[monitorindex], decimals=2)
                self.entrymonitor.delete(0, 'end')
                self.entrymonitor.insert(0,monitorwave)
                self.ax.lines.pop(-1)
                self.ax.axvline(x=monitorwave, lw=2, color='blue', alpha  = 0.5)
            else:
                msg = "Monitored wavelength must be within the detected range.  Range is " + str(xmin) + " to " + str(xmax) + " nm."
                self.entrymonitor.delete(0, 'end')
                self.entrymonitor.insert(0, monitorwave)
                popupmsg(msg)
        except:
            self.entrymonitor.delete(0, 'end')
            self.entrymonitor.insert(0, monitorwave)

fig, ax = plt.subplots()
spectro = Spec(ax)

# animate
ani = animation.FuncAnimation(fig, spectro.update, interval=10, blit=False)
spectro.mainloop()
