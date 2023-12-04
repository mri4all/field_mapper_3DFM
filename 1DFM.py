'''
   Copyright 2021 Aaron R. Purchase

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

    Parts of this code is modified from:
    1) pyTHM1176 at https://github.com/Hyperfine/pyTHM1176
    2) simple g-code stream at https://github.com/grbl/grbl

    Author: Aaron R. Purchase
    Date: 5 May 2021
'''

import serial
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

import time

import usbtmc as backend
import pyTHM1176.api.thm_usbtmc_api as thm_api
import numpy as np

params = {"trigger_type": "single", 'range': '0.1T', 'average': 30000, 'format': 'ASCII'}


if __name__ == "__main__":

    thm = thm_api.Thm1176(backend.list_devices()[0], **params)
    # Get device id string and print output. This can be used to check communications are OK
    device_id = thm.get_id()
    for key in thm.id_fields:
        print('{}: {}'.format(key, device_id[key]))
    
# Open grbl serial port
s = serial.Serial('COM8',115200)
    
# Wake up grbl
s.write(b"\r\n\r\n")
time.sleep(2)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input
    
w = 1

# STEPPER CONFIGURATION
# IMP: magnet axis (x,y,z) is different than CNC axis (X,Y,Z)
x_forwords = 'G91 X-0.6402 F100000' #negative is into magnet, longitudinal axis. 0.164 steps/mm. 'G91 X-0.164 F100000'
x_backwords = 'G91 X0.6402 F100000' #'G91 X0.164 F100000'
y_forwords = 'G91 Y0.6415 F100000' #'G91 Y-0.164 F100000'
y_backwords = 'G91 Y-0.6415 F100000' #'G91 Y0.164 F100000'
z_forwords = 'G91 Z0.1596 F100000' #1.3888 steps/mm.#'G91 Z-1.3888 F100000'
z_backwords = 'G91 Z-0.1596 F100000' #'G91 Z1.3888 F100000'

# Stream g-code to grbl
z=z_forwords
y=y_forwords
x=x_forwords

# Set initial 3D map size
n_sizeX = 50
Bfield_3D_array=np.array([])

# Move to front, bottom-left corner of map. Code finishes at back, top-right.
half_stepsX = int((n_sizeX-1)/2)
for z_half in range(0, half_stepsX):
    s.write(z_backwords.encode('utf-8') + '\n'.encode('utf-8'))
    grbl_out = s.readline()
    s.write(z_backwords.encode('utf-8') + '\n'.encode('utf-8'))
    grbl_out = s.readline()
    s.write(z_backwords.encode('utf-8') + '\n'.encode('utf-8'))
    grbl_out = s.readline()
    
time.sleep(10)
thm.make_measurement(**params)
meas=thm.last_reading
measurements=list(meas.values())
Bx=np.array(measurements[0])*10000;
By=np.array(measurements[1])*10000;
Bz=np.array(measurements[2])*10000;
Bmod=np.sqrt(Bx**2+By**2+Bz**2)
print(w , Bx[0], By[0], Bz[0], Bmod[0])
Bfield_3D_array=np.append(Bfield_3D_array,Bmod[0])

# Time to map it out in 3D
for k in range(0, n_sizeX-1):
            w=w+1
            #print("x is %s" % (x))
            #print("___")
            s.write(z.encode('utf-8') + '\n'.encode('utf-8'))
            grbl_out = s.readline()
            s.write(z.encode('utf-8') + '\n'.encode('utf-8'))
            grbl_out = s.readline()
            s.write(z.encode('utf-8') + '\n'.encode('utf-8'))
            grbl_out = s.readline()
            time.sleep(1)
            thm.make_measurement(**params)
            meas=thm.last_reading
            measurements=list(meas.values())
            Bx=np.array(measurements[0])*10000;
            By=np.array(measurements[1])*10000;
            Bz=np.array(measurements[2])*10000;
            Bmod=np.sqrt(Bx**2+By**2+Bz**2)
            print(w , Bx[0], By[0], Bz[0], Bmod[0])
            Bfield_3D_array=np.append(Bfield_3D_array,Bmod[0])
        
            
#rewind; brings back to its own center (must calibrate)
n_rewind = (n_sizeX - 1 )/2
for i in range(0, int(n_rewind)):
    s.write(z_backwords.encode('utf-8') + '\n'.encode('utf-8'))
    grbl_out = s.readline()
    s.write(z_backwords.encode('utf-8') + '\n'.encode('utf-8'))
    grbl_out = s.readline()
    s.write(z_backwords.encode('utf-8') + '\n'.encode('utf-8'))
    grbl_out = s.readline()
        