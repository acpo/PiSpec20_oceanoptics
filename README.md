# PiSpec20_OceanOptics
A Python interface for Ocean Optics spectrometers designed to proved the functions of a Spectronic 20 spectrophotometer.
## Project Goals and Motivations  
The goal of this project was to replace the old Spec 20s in our teaching laboratories with equivalent functionality in 
modern equipment.  Choices of hardware and software were driven largely by familiarity.  The choice of the Raspberry Pi was 
to make an effectively disposable computer.  I picked Python 3.x (the older branch works on Python 2.7 also) for simplicity in migrating to different hardware.  What I created here is a simple frontend for the spectrometer suitable for use by relatively untrained undergraduate students.
## Project Audience  
The project was written to support undergraduate laboratories, so really this repository is for people looking for a frontend 
to run their spectrometer.  However, the functionality of the project can readily be expanded to take advantage of the 
spectrometer features.  This code takes care of collecting the spectra, everything else is just manipulations in code.  Simple changes in the code shift the interface from having lots of things chosen for you to needing to make lots of choices.   For example, there is a 'Save Button' commented out in the code. If you uncomment the 3 lines of the GUI for the button, the Save function is fully implemented.  
## PiSpec20 Requirements  
I wrote this on a Raspberry Pi 3b+.  The current version was updated on Python 3.9 and 3.11.  Raspbian OS *Bullseye* was used for testing.  The newer (in 2024) *Bookworm* OS also works but is slow on a 3b+.  
For Windows or Mac you will need to make small changes to the code to deal with OS peculiarities.  You will need to possess an Ocean Optics spectrometer.  
*extra Windows requirement:  
[Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) is required before installing Python-Seabreeze    
See the documentation at the [python-seabreeze documents](https://python-seabreeze.readthedocs.io/en/latest/install.html#operating-system-dependent-setup)*  
Installation is fairly simple:  I was able to install Seabreeze, numpy, matplotlib, and directly run the included .py file.  

### Libraries  
- `pip3 install seabreeze`  (https://github.com/ap--/python-seabreeze  or the Conda forge)
- run the seabreeze setup script `seabreeze_os_setup` to add the udev rules
- `pip3 install numpy`
- `pip3 install matplotlib`
- (*May 2024*) may need to also get `sudo apt-get install python3-pil.imagetk` to address an import error from matplotlib  
- Tkinter (usually automatically in Python)
#### Optional libraries
- SeaBreeze  (https://sourceforge.net/projects/seabreeze/  if you want to play with the backend)
- python-virtualenv  -- if you want to use *venv*  (required for some newer Linux)
### Files to install
- only one python file to get ¯\\_(ツ)_/¯ 
### Other Hardware  
- a USB connected Ocean Optics spectrometer  
- a light source if you are going to do absorbance experiments
## Supported Devices  
### Directly tested  
| Manufacturer  | Spectrometer  | Works ?       |  
| ------------- | ------------- | ------------- |  
| Ocean Insight | HR 4000       |     yes       |  
| Ocean Insight | HR 2000 plus  |     yes       |  
| Ocean Insight | USB 2000      |     yes       | 

### Should work with SeaBreeze (Ocean Insight products)  
| Spectrometer | cseabreeze | pyseabreeze|  
| ------------ | :--------: | :--------: |  
|HR2000 |x | x |
|HR2000PLUS |x | x |
|HR4000 |x | x |
|JAZ |x | x |
|MAYA2000 |x | x |
|MAYA2000PRO |x | x |
|MAYALSL |x | x |
|NIRQUEST256 |x | x |
|NIRQUEST512 |x | x |
|QE65000 |x | x |
|QE-PRO |x | x |
|STS |x | x |
|TORUS |x | x |
|USB2000 |x | x |
|USB2000PLUS |x | x |
|USB4000 |x | x |
|USB650 | no | no |
|SPARK |x | x |  

## How to Help  
I don't write in Python for a living, nor particularly do a lot of programming.  But the project works.   The code could probably be more efficient but free software is free.  
If you wish to contribute please contact me.
## License  
MIT License.  This project relies on Python-Seabreeze which uses the MIT License.
