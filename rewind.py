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
import time
# Open grbl serial port
# s = serial.Serial('/dev/ttyACM0',115200)
s = serial.Serial('COM8',115200)
s.write(b"\r\n\r\n")
time.sleep(2)   # Wait for grbl to initialize
s.flushInput()  # Flush startup text in serial input
z_forwords = 'G91 Z0.1596 F100000' #1.3888 steps/mm.#'G91 Z-1.3888 F100000'  # AWAY FROM MOTOR
z_backwords = 'G91 Z-0.1596 F100000' #'G91 Z1.3888 F100000'  # TOWARDS MOTOR

x_forwords = 'G91 X-0.6402 F100000' #negative is into magnet, longitudinal axis. 0.164 steps/mm. 'G91 X-0.164 F100000'
# x_forwords is TOWARDS MOTOR
x_backwords = 'G91 X0.6402 F100000' #'G91 X0.164 F100000'  # AWAY FROM MOTOR

y_forwords = 'G91 Y0.6415 F100000' #'G91 Y-0.164 F100000'  # AWAY FROM MOTOR
y_backwords = 'G91 Y-0.6415 F100000' #'G91 Y0.164 F100000'  # TOWARDS MOTOR

n_rewind = 80
for i in range(0, int(n_rewind)):
    s.write(x_backwords.encode('utf-8') + '\n'.encode('utf-8'))
    grbl_out = s.readline()

s.close()
print("Finished")