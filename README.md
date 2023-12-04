# 3DFM Updates
v1.0: Automated 3D magnetic flux density mapping system v1.0
v2.0: Recents updates from the MRI4ALL Hackathon in NYC
	- generalized 3D mapping procedure (cube, sphere, surface of sphere)
	- mapping permanent magnet constructions, passive shims, or 3 axis switched gradient coils (data included)

#Required software and Hardware
- Ubuntu 20.04 / Windows 10 or 11
- Python 3 or higher (very easy setup with PyCharm and relevant libraries)
- Arduino UNO Rev3: https://store.arduino.cc/usa/arduino-uno-rev3
- Arduino gShield: https://synthetos.com/project/grblshield
- Any 3D CNC rail set up or 3D printer arm
	- v1.0: Shapeoko 2 axis
	- v2.0: MRI4ALL hackathon used 3x, 30 cm linear CNC stages attached perpendicularly.
- USB probe 
	- Metrolab THM1176 used here. 

#Installation
1. Install single trigger code for the THM1176 probe (https://github.com/Hyperfine/pyTHM1176/tree/cedh/single_trig/)
	- place all 'pyTHM1176' subdirectory files into the 3DFM folder.
	- read pyTHM1176 notes (must have correct drivers installed using Zadig)
	
2. Flash GRBL 1.1h (i.e. the *.hex file) to the Arduino UNO.
	- see https://github.com/gnea/grbl/releases/
	- xLoader (https://github.com/binaryupdates/xLoader) [Windows]
	
3. Change 's = serial.Serial('COM8', 115200)' of the "measure_table.py" code to match your Arduino UNO port.
	- In Windows, use Device Manager to determine COM port number.

4. Power ON the Arduino + gShield using a 24 V power supply unit
	- connect probe USB
	- connect CNC USB

5. Choose the path of points you want to measure. 
	- change the path for input table name ("

6. Read through comments in "measure_table.py" and make changes before running code.
	- use 'rewind.py' to move probe without measurements

7. Hit the play button.

#Notes
- v1.0 code still included. 
	- 3DFM.py will map in a zig-zag pattern over a defined volume.
	- default mapping range is 13.5 cm x 13.5 cm x 1 cm in steps of 3 mm x 3 mm x 1 mm.

#Future work
- GUI
- various functions (homing, etc)
- 3D visuals of mapping region and field plotting during process
