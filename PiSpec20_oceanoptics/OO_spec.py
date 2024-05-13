# version May 2024

## start Shared Imports (OO/Stellarnet)
from sys import version_info
if version_info.major == 2:
    # use Python 2.7 style
    import Tkinter as tk
    import ttk
elif version_info.major == 3:
    # use Python 3.x style
    import tkinter as tk
    from tkinter import ttk

from tkinter import Spinbox
from tkinter import messagebox
from tkinter.filedialog import asksaveasfilename

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from matplotlib import style
style.use("ggplot")
plt.rcParams['axes.facecolor']='#F8F8F8'
#plt.rcParams['lines.color']='blue'
plt.rcParams['figure.figsize'] = [8.0, 6.0]
LARGE_FONT= ("Verdana", 12)
NORM_FONT= ("Verdana", 10)

import numpy as np

import os #for filename and path handling
import csv  #easier file writing
import gc  #garbage collection
## end Shared Imports

## OceanOptics Specific Imports
import seabreeze.spectrometers as sb
##

## start OceanOptics set up functions
# Enumerate spectrometer
try:
    spectrometer = sb.Spectrometer.from_serial_number()
except:
    messagebox.showerror("Error", "No spectrometer attached")
    exit()
    
# Spectrometer data collectors
def get_wavelengths():
    spec_x = spectrometer.wavelengths()
    return spec_x
def get_intensities():
    spec_y = spectrometer.intensities(correct_dark_counts=False, correct_nonlinearity=False) #dark counts might need to be false
    return spec_y
## end OceanOptics set up functions

class App(tk.Frame):
    def __init__(self, master=None, **kwargs):
        tk.Frame.__init__(self, master, **kwargs)
#Spectrometer initial setup
        self.wavelengths = np.around(get_wavelengths(), decimals=3) #round wavelengths to practical limits
        self.ydata = np.array(get_intensities())
        self.xmin = np.around(min(self.wavelengths), decimals=3)
        self.xminlimit = self.xmin
        self.xmax = np.around(max(self.wavelengths), decimals=3)
        self.xmaxlimit = self.xmax
        self.ymin = np.around(min(self.ydata * 0.8), decimals=3) #ymin is the display limit, data_min*0.8 to give a margin
        self.ymax = np.around(max(self.ydata * 1.1), decimals=3)
        self.waveres = np.around(self.wavelengths[1] - self.wavelengths[0], decimals=3)
        self.IntTime = 20000 #set in microseconds, this is 20ms set as a "reasonable" default value
        spectrometer.integration_time_micros(self.IntTime)  #send IntTime to spectrograph
        self.minIntTime = spectrometer.integration_time_micros_limits[0]/1000  # new function name in 2023 SeaBreeze
        if self.minIntTime < 4:
            self.minIntTime = 4  # most OceanOptics spectrometers actually have a 4 ms minimum integration time
        self.max_intensity = spectrometer.max_intensity  #fullscale limit
        self.Averages = 1   #set default averages to a reasonable value
        
        #preload dark and incident values
        self.dark = np.zeros(len(self.wavelengths))     #dummy values set to zero
        self.incident = np.ones(len(self.wavelengths))  #dummy values to prevent error in Absorbance when no dark recorded
        self.DisplayCode = 0      #start in raw intensity mode

#GUI entries
        self.menu_left = tk.Frame(self, width=150, bg="#ababab")
        #menus are grid arranged
        # left display area -- Spectrometer Controls
        self.menu_left_upper = tk.Frame(self.menu_left, width=150, height=150, bg="grey")
        
        self.heading = tk.Label(self.menu_left_upper, text="Spectrometer Controls")
        self.heading.grid(column=0, row=0, columnspan=2)
        
        self.menu_left_upper.pack(side="top", fill="both", expand=False)

        self.labelint = tk.Label(self.menu_left_upper, text='Integration Time (ms)', relief='ridge')    
        self.labelint.grid(column=0, row=1, pady=2)
        self.entryint = tk.Entry(self.menu_left_upper, width='6')
        self.entryint.grid(column=1, row=1)
        self.entryint.insert(0, self.IntTime/1000)  # Different in OO!!! IntTime is in microseconds in OO but milliseconds on StellarNet
        self.entryint.bind('<Return>', self.EntryInt_return) and self.entryint.bind('<Tab>', self.EntryInt_return)

        self.labelavg = tk.Label(self.menu_left_upper, text='# of spectra to average', relief='ridge', width='17', wraplength='100')
        self.labelavg.grid(column=0, row=2, pady=2)
        self.entryavg = tk.Entry(self.menu_left_upper, width='4')
        self.entryavg.grid(column=1, row=2, pady=2)
        self.entryavg.insert(0, self.Averages)
        self.entryavg.bind('<Return>', self.EntryAvg_return) and self.entryavg.bind('<Tab>', self.EntryAvg_return)
        
        self.labelxmin = tk.Label(self.menu_left_upper, text='Minimum wavelength', relief='ridge')
        self.labelxmin.grid(column=0, row=3, pady=2)
        self.xminentry = tk.Entry(self.menu_left_upper, width='7')
        self.xminentry.grid(column=1, row=3, pady=2)
        self.xminentry.insert(0, self.xmin)
        self.xminentry.bind('<Return>', self.xScaleChange) and self.xminentry.bind('<Tab>', self.xScaleChange)
        
        self.labelxmax = tk.Label(self.menu_left_upper, text='Maximum wavelength', relief='ridge')
        self.labelxmax.grid(column=0, row=4, pady=2)
        self.xmaxentry = tk.Entry(self.menu_left_upper, width='7')
        self.xmaxentry.grid(column=1, row=4, pady=2)
        self.xmaxentry.insert(0, self.xmax)
        self.xmaxentry.bind('<Return>', self.xScaleChange) and self.xmaxentry.bind('<Tab>', self.xScaleChange)
        
        self.button_dark = tk.Button(self.menu_left_upper, text='Measure Dark', background='light grey')
        self.button_dark.grid(column=0, row=5, pady=2)
        self.button_dark.bind('<ButtonRelease-1>', self.getdark)
        self.button_incident = tk.Button(self.menu_left_upper, text='Measure 100% T', background='light grey') 
        self.button_incident.grid(column=1, row=5, pady=2)
        self.button_incident.bind('<ButtonRelease-1>', self.getincident)
        
        self.button_AbMode = tk.Button(self.menu_left_upper, text='Absorbance Mode (off)', background = 'light grey')
        self.button_AbMode.grid(column=1, row=6, pady=2)
        self.button_AbMode.bind('<ButtonRelease-1>', self.AbMode)

        self.labelmonitor = tk.Label(self.menu_left_upper, text='Wavelength to monitor (nm)', font=LARGE_FONT)
        self.labelmonitor.grid(column=0, row=7, pady=2)

        self.monitorwave = np.median(self.wavelengths)  #set monitor wavelength to middle of hardware range
        self.monitorindex = np.searchsorted(self.wavelengths, self.monitorwave, side='left')
        self.entrymonitor = tk.Entry(self.menu_left_upper, width='7')
        self.entrymonitor.grid(column=1, row=7, pady=2)
        self.entrymonitor.insert(0, np.round(self.wavelengths[self.monitorindex], decimals=2))
        self.entrymonitor.bind('<Return>', self.entrymonitor_return) and self.entrymonitor.bind('<Tab>', self.entrymonitor_return)
        self.labelmonitor2 = tk.Label(self.menu_left_upper, text="press <Enter> to set new wavelength")
        self.labelmonitor2.grid(column=0, row=8, pady=2)

        self.button_reset_y = tk.Button(self.menu_left_upper, text='Reset Y axis scale', background='light blue')
        self.button_reset_y.grid(column=0, row=9, pady=10)
        self.button_reset_y.bind('<ButtonRelease-1>', self.reset_y)
##
##        self.button_saveFile = tk.Button(self.menu_left_upper, text='Save File', background='light slate blue')
##        self.button_saveFile.grid(column=0, row=12, pady=3)
##        self.button_saveFile.bind('<ButtonRelease-1>', self.saveFile)
        

# right display area -- Spectrograph Plot Area
        self.some_title_frame = tk.Frame(self, bg="#dfdfdf")
        self.some_title = tk.Label(self.some_title_frame, text="Spectrograph Window", bg="#dfdfdf")
        self.some_title.pack()
        #buttons at top of Spectrum region        
        self.btn = tk.Button(self.some_title_frame, text='Start', command=self.on_click)
        self.btn.pack(side=tk.RIGHT)
        self.quitbutton = tk.Button(self.some_title_frame, text='Quit', command=self.ButtonQuit)
        self.quitbutton.pack(side=tk.RIGHT)
      
        #first two lines give a functioning empty box
        self.canvas_area = tk.Canvas(self, width=300, height=200, background="#ffffff")
        self.canvas_area.grid(row=1, column=1)
        
        #lower status bar
        self.status_frame = tk.Frame(self)
        self.status = tk.Label(self.status_frame, text = spectrometer)
        self.status.pack(fill="both", expand=False)

        #set locations of the major areas to the corners of the box
        self.menu_left.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.some_title_frame.grid(row=0, column=1, sticky="ew")
        self.canvas_area.grid(row=1, column=1, sticky="nsew") 
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

#Create plot area
        #create plot object and draw it with empty data before starting matplotlib line artists
        # 'ax1' is ax"one" not a letter
        self.fig = plt.Figure()
        self.ax1 = self.fig.add_subplot(111)
        self.line, = self.ax1.plot([], [], lw=1, color='blue') #creates empty line !! comma is important for Blit
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=1)

#Axis limits. Get from the spectrograph data
        self.ax1.set_ylim(self.ymin, self.ymax)
        self.ax1.set_xlim(self.xmin, self.xmax) 
        self.ax1.set_xlabel('Wavelength (nm)')
        self.ax1.grid(True, color='0.3', ls='dotted')  # places dark grid on spectrum display
#Create the line artist objects for Blit
        monitor = np.round(self.ydata[self.monitorindex], decimals=3)
        self.text = self.ax1.annotate(monitor, (1, 1), xycoords="axes fraction", xytext=(10, -10),
                                      textcoords="offset points", ha="right", va="top", fontsize = 14, animated = True,)
        self.ax1.axvline(x=self.monitorwave, lw=2, color='blue', alpha  = 0.5)
        self.bm = BlitManager(self.fig.canvas, [self.line, self.text])

#end artist creation

## GUI end of entries


### start OceanOptics specific defs
# SET CONFIGURATION
    def setconfig(self):
        spectrometer.integration_time_micros(self.IntTime)
        # write new configuration to dialog        
        self.entryint.delete(0, "end")
        self.entryint.insert(0,self.IntTime / 1000)  #write ms, but IntTime is microseconds
        self.entryavg.delete(0, "end")
        self.entryavg.insert(0,self.Averages)  #set text in averages box       
## end OceanOptics specific defs
        
## start Shared (OO/Stellarnet) defs
    def on_click(self):
        # Start button will start infinite cycle on whole spectrum or start an individual time series.
        gc.collect()
        self.bm = BlitManager(self.fig.canvas, [self.line, self.text]) 
        self.btn.config(text='Running')
        return self.update_graph()

    def update_graph(self):
        # if DisplayCode = 0 then do Raw Values;  else do Absorbance
        self.canvas.draw()  # guarantees that all lines and scaling get reset

        while self.DisplayCode == 0:
            ydata = get_intensities()
            ydata = np.array(ydata, dtype=float)
            monitor = np.round(ydata[self.monitorindex], decimals=3)
            self.line.set_data(self.wavelengths, ydata) # update matplotlib line data
            self.text.set_text(f"{monitor}")
            self.bm.update()  #redraw with blit manager call
            gc.collect()  # garbage collector
 
        else:
            np.seterr(divide='ignore', invalid='ignore')
            while self.DisplayCode == 1:
                ydata = get_intensities()
                ydata = np.array(ydata, dtype=float)
                ydata = np.log10((self.incident - self.dark) / (ydata - self.dark))
                monitor = np.round(ydata[self.monitorindex], decimals=3)
                self.line.set_data(self.wavelengths, ydata)
                self.text.set_text(f"{monitor}")
                self.bm.update()  # blit manager call
                gc.collect()  # garbage collector


    def getdark(self, event):
        dark = get_intensities()
        self.dark = np.array(dark, dtype=float)
        self.button_dark.configure(background = 'light green')

    def getincident(self,event):
        incident = get_intensities()
        self.incident = np.array(incident, dtype=float)
        self.button_incident.configure(background = 'light green')
      
    def AbMode(self, event):
        if self.DisplayCode == 1:
            self.DisplayCode = 0
            self.ax1.set_ylabel('Counts')
            self.button_AbMode.configure(text='Absorbance Mode (off)', background = 'light grey')
            self.reset_y(self)
            self.line.set_color('blue')
            self.update_graph()
        else:
            self.DisplayCode = 1
            self.ax1.set_ylabel('Absorbance')
            self.ax1.set_ylim(-0.1,1.2)
            self.button_AbMode.configure(text='Absorbance Mode (on)', background = 'light green')
            self.line.set_color('red')

    def reset_y(self, event):
        if self.DisplayCode == 0:
            index_xmin = np.searchsorted(self.wavelengths, self.xmin, side='left')
            index_xmax = np.searchsorted(self.wavelengths, self.xmax, side='left')
            ydata = np.around(get_intensities(), decimals=2)
            self.ymin = np.around(min(ydata[index_xmin:index_xmax])*0.9, decimals=2)
            self.ymax = np.around(max(ydata[index_xmin:index_xmax])*1.1, decimals=2)
            self.ax1.set_ylim(self.ymin, self.ymax)
            self.canvas.draw() 
        else:
            pass


    def EntryInt_return(self, event):
        IntTimeTemp = self.entryint.get()
        if IntTimeTemp.isdigit() == True:
            if int(IntTimeTemp) > 65000:
                msg = "The integration time must be 65000 ms or smaller.  You set " +(IntTimeTemp)
                self.setconfig()
                messagebox.showerror("Entry error", msg)
            elif int(IntTimeTemp) < self.minIntTime:
                msg = "The integration time must be greater than 4 ms.  You set " +(IntTimeTemp)
                self.setconfig()
                messagebox.showerror("Entry error", msg)
            else:
                self.IntTime = int(IntTimeTemp) * 1000  #convert ms to microseconds
                self.setconfig()
        else:
            msg = "Integration time must be an integer between 4 and 65000 ms.  You set " +str(IntTimeTemp)
            self.setconfig()
            messagebox.showerror("Entry error", msg)

    def EntryAvg_return(self, event):
        ## averaging needs to be implemented here in code
        #  cseabreeze has average working, but python-seabreeze doesn't (2019)
        #  averaging is only available on newer OO models 
        self.Averages = self.entryavg.get()
        if self.Averages.isdigit() == True:
            self.Averages = int(float(self.Averages))
            self.setconfig()
        else:
            msg = "Averages must be an integer.  You tried " + str(self.Averages) + ".  Setting value to 1."
            self.Averages = 1
            self.setconfig()
            messagebox.showerror("Entry error", msg)

    def xScaleChange(self, event):  #always do both xmin and xmax on change of either
        xmintemp = self.xminentry.get()
        xmaxtemp = self.xmaxentry.get()
        try:  
            float(xmintemp)
            xmintemp = float(self.xminentry.get())
            float(xmaxtemp)
            xmaxtemp = float(self.xmaxentry.get())
            if (xmintemp < self.xmax) and (xmaxtemp > self.xmin) and (xmintemp >= self.xminlimit) and (xmaxtemp <= self.xmaxlimit):
                self.xmin = xmintemp
                self.xminentry.delete(0, 'end')
                self.xminentry.insert(0, self.xmin)  #set text in xmin box
                self.xmax = xmaxtemp
                self.xmaxentry.delete(0, 'end')
                self.xmaxentry.insert(0, self.xmax)  #set text in xmax box
                self.ax1.set_xlim(self.xmin, self.xmax)  # set the new value on plot area
                self.canvas.draw()
            else:
                msg = "Minimum wavelength must be greater than " + str(self.xminlimit) + "nm and maximum smaller than " + str(self.xmaxlimit) + "nm.  Also, max greater than min.  You entered: min = " + str(xmintemp) + " nm and max = " + str(xmaxtemp) + " nm."
                self.xminentry.delete(0, 'end')
                self.xminentry.insert(0, self.xmin)  #reset original xmin in box
                self.xmaxentry.delete(0, 'end')
                self.xmaxentry.insert(0, self.xmax)  #reset original xmax in box
                messagebox.showerror("Entry error", msg)
        except:
            self.xminentry.delete(0, 'end')
            self.xminentry.insert(0, self.xmin)  #reset original xmin in box
            self.xmaxentry.delete(0, 'end')
            self.xmaxentry.insert(0, self.xmax)  #reset original xmax in box

    def entrymonitor_return(self, event):
        monitorwavetemp = self.entrymonitor.get()
        try:
            float(monitorwavetemp)  #can string be converted to float?
            if (float(monitorwavetemp) < self.xmax) and (float(monitorwavetemp) > self.xmin): #entry is within current bounds
                self.monitorindex = np.searchsorted(self.wavelengths, monitorwavetemp, side='left')
                self.monitorwave = np.around(self.wavelengths[self.monitorindex], decimals=2)
                self.entrymonitor.delete(0, 'end')
                self.entrymonitor.insert(0,self.monitorwave)
                self.ax1.lines[1].remove()
                self.ax1.axvline(x=self.monitorwave, lw=2, color='blue', alpha  = 0.5)
                self.canvas.draw()
            else:
                msg = "Monitored wavelength must be within the detected range.  Range is " + str(self.xmin) + " to " + str(self.xmax) + " nm."
                self.entrymonitor.delete(0, 'end')
                self.entrymonitor.insert(0, self.monitorwave)
                messagebox.showerror("Entry error", msg)
        except:
            self.entrymonitor.delete(0, 'end')
            self.entrymonitor.insert(0, self.monitorwave)

    def monitoraction(self, event):
        self.monitorwave = self.entrymonitor.get()
        self.ax1.axvline(x=self.monitorwave, lw=2, color='blue', alpha  = 0.5)

    def saveFile(self, event):
        filenameforWriting = asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"),("All files", "*.*")])
        if not filenameforWriting:
            pass  #exits on Cancel
        else:
            path_ext = os.path.splitext(filenameforWriting)
            xdata = np.asarray(self.wavelengths)
            ydata = get_intensities()
            ydata = np.asarray(ydata)
            file_to_write = str(path_ext[0] + path_ext[1])

            if self.DisplayCode == 0:
                fileheader = "# Wavelength (nm), Count"
            else:
                fileheader = "# Wavelength (nm), Absorbance"
                
            np.savetxt(file_to_write, np.transpose([xdata, ydata]), delimiter=',', newline='\n', header=fileheader, comments='')

    def ButtonQuit(self):
        self.StopCode = True
        App.destroy(self)
        tk.Frame.quit(self)
        exit(0)
        
## end Shared (OO/Stellarnet) defs
        
class BlitManager:
    def __init__(self, canvas, animated_artists=()):
        """
        Parameters
        ----------
        canvas : FigureCanvasAgg
            The canvas to work with, this only works for sub-classes of the Agg
            canvas which have the `~FigureCanvasAgg.copy_from_bbox` and
            `~FigureCanvasAgg.restore_region` methods.

        animated_artists : Iterable[Artist]
            List of the artists to manage
        """
        self.canvas = canvas
        self._bg = None
        self._artists = []

        for a in animated_artists:
            self.add_artist(a)
        # grab the background on every draw
        self.cid = canvas.mpl_connect("draw_event", self.on_draw)

    def on_draw(self, event):
        """Callback to register with 'draw_event'."""
        cv = self.canvas
        if event is not None:
            if event.canvas != cv:
                raise RuntimeError
        self._bg = cv.copy_from_bbox(cv.figure.bbox)
        self._draw_animated()

    def add_artist(self, art):
        """
        Add an artist to be managed.

        Parameters
        ----------
        art : Artist

            The artist to be added.  Will be set to 'animated' (just
            to be safe).  *art* must be in the figure associated with
            the canvas this class is managing.

        """
        if art.figure != self.canvas.figure:
            raise RuntimeError
        art.set_animated(True)
        self._artists.append(art)

    def _draw_animated(self):
        """Draw all of the animated artists."""
        fig = self.canvas.figure
        for a in self._artists:
            fig.draw_artist(a)

    def update(self):
        """Update the screen with animated artists."""
        cv = self.canvas
        fig = cv.figure
        # paranoia in case we missed the draw event,
        #...let's try removing the paranoia??
        if self._bg is None:
            self.on_draw(None)
        else:
            # restore the background
            cv.restore_region(self._bg)
            # draw all of the animated artists
            self._draw_animated()
            # update the GUI state
            cv.blit(fig.bbox)
        # let the GUI event loop process anything it has to do
        cv.flush_events()



def main():
    root = tk.Tk()
    root.wm_title("Ocean Optics Spectrometer Control")
    app = App(root)
    app.pack()
    root.mainloop()

if __name__ == '__main__':
    main()
