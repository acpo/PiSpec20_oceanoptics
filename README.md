# PiSpec20_OceanOptics
A Python interface for Ocean Optics spectrometers designed to proved the functions of a Spec20
## Project Goals and Motivations  
The goal of this project was to replace the old Spec 20s in our teaching laboratories with equivalent functionality in 
modern equipment.  Choices of hardware and software were driven largely by familiarity.  The choice of the Raspberry Pi was 
to make an effectively disposable computer.  I picked Python 2.x for simplicity in migrating to different hardware.  What I 
created here is a simple frontend for the spectrometer suitable for use by relatively untrained undergraduate students.
## Project Audience  
The project was written to support undergraduate laboratories, so really this repository is for people looking for a frontend 
to run their spectrometer.  However, the functionality of the project can readily be expanded to take advantage of the 
spectrometer features.  This code takes care of collecting the spectra, everything else is just manipulations in code.
## PiSpec20 Requirements  
I wrote this on a Raspberry Pi 3b+.  For Windows or Mac you will need to make small changes to the code to deal with OS peculiarities.  
### Libraries  
- SeaBreeze  
- numpy  
- python-matplotlib  
- python-flask  
- python-virtualenv  
- Tkinter  
### Files to install
- ...
### Other Hardware  
- a USB connected Ocean Optics spectrometer  
- a light source if you are going to do absorbance experiments
## How to Help  
I don't write in Python for a living, nor particularly do a lot of programming.  And it shows in the code.  This is 
also a work in progress.  
If you wish to contribute please contact me.
## License  
not sure
