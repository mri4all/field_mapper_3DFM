import serial
import sys
import os
import time
import pandas as pd
import numpy as np
import usbtmc as backend
import pyTHM1176.api.thm_usbtmc_api as thm_api


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))

# ################ SETUP #########################
# Note: The table should give the amounts to move in mm. No partial mm are acceptable
table_filename = "movement_paths/sphere_35radius_64points_1perPos.csv"
output_filename = "measurements/sphere_35radius_64points_1perPos_measurements_passiveShim.csv"
# table_filename = "movement_paths/20cube_2samples_1measurements_per_pos.csv"
# output_filename = "measurements/test_cube.csv"
move_motors = True
move_in_increments = False
send_external_trigger = False
measure_probe = True  # NB: before changing this, make sure you aren't overwriting a previous measurement output file!
default_measurement_delay = 0.5  # default time delay for measurement, often will be overwritten by the table file

# Trigger commands to trigger the spindle direction pin
trigger_cmd_hi = "M4 S0".encode('utf-8') + '\n'.encode('utf-8')
trigger_cmd_lo = "M3 S0".encode('utf-8') + '\n'.encode('utf-8')

direction_step_sizes = {  # These were calibrated manually
    "dx": 0.6402,
    "dy": 0.6415,
    "dz": 0.1596
}
if __name__ == "__main__":

    # ################# SETUP MOTORS ########################
    # Open grbl serial port
    if move_motors or send_external_trigger:
        s = serial.Serial('COM8', 115200)
        s.write(b"\r\n\r\n")
        time.sleep(2)   # Wait for grbl to initialize
        s.flushInput()  # Flush startup text in serial input

        # If sending external pulses, set the output pin to low to prepare for pulses
        if send_external_trigger:
            s.write(trigger_cmd_lo)
            s.readline()

    # ################## SETUP PROBE #######################
    if measure_probe:
        params = {"trigger_type": "single", 'range': '0.1T', 'average': 30000, 'format': 'ASCII'}

        thm = thm_api.Thm1176(backend.list_devices()[0], **params)
        # Get device id string and print output. This can be used to check communications are OK
        device_id = thm.get_id()
        for key in thm.id_fields:
            print('{}: {}'.format(key, device_id[key]))

    # #########################################
    # Load data file
    df_table = pd.read_csv(table_filename)

    # Set up save file
    print("Saving measurement to file", output_filename)
    string_to_write = ",".join(["index", "dx", "dy", "dz", "Bx", "By", "Bz", "Bmod", "x", "y", "z", "trigger", "\n"])
    with open(output_filename, "w") as f:
        f.write(string_to_write)

    # #########################################
    for index, row in df_table.iterrows():
        command_num = row["index"]
        if "delay" in row:
            measurement_delay = row["delay"]
        else:
            measurement_delay = default_measurement_delay
        print(f"\n{int(command_num)}", "- move to:", row["x"], row["y"], row["z"], "---------------------------------------")
        print("\tdelay", measurement_delay, "--- dx, dy, dz:", row["dx"], ",", row["dy"], ",", row["dz"])
        # Cycle through each direction (x, y, z)
        amts_to_move = []
        movement_command = "G91"
        for direction in direction_step_sizes.keys():
            amt_to_move_mm = row[direction]
            if amt_to_move_mm == 0:
                continue

            # Do the movement:
            if move_in_increments:
                # assert amt_to_move_mm % 1 == 0, f"Found non-integer step size for {direction}: {amt_to_move_mm}"
                num_steps = int(np.abs(amt_to_move_mm))
                if np.sign(amt_to_move_mm) > 0:
                    sign = ""
                else:
                    sign = "-"
                movement_command = f"G91 {direction.replace('d','').upper()}{sign}{direction_step_sizes[direction]} F100000"
                print("\tSTART: incremental move", direction, "move:", amt_to_move_mm,
                      "--> CMD:", movement_command, "\tnum steps:", num_steps)
                if move_motors:
                    amount_moved = 0
                    for step_idx in range(num_steps):
                        amount_moved += 1
                        s.write(movement_command.encode('utf-8') + '\n'.encode('utf-8'))
                        grbl_out = s.readline()
                    amount_left_to_move = np.abs(amt_to_move_mm) - amount_moved
                    scaled_movement = amount_left_to_move * direction_step_sizes[direction]
                    movement_command = f"G91 {direction.replace('d', '').upper()}{sign}{scaled_movement} F100000"
                    print("\tFINAL: incremental move", direction, "move:", amount_left_to_move,
                          "--> CMD:", movement_command)
                    s.write(movement_command.encode('utf-8') + '\n'.encode('utf-8'))
                    grbl_out = s.readline()
                    print(f"\tFinished, total movement: {sign}{amount_left_to_move + amount_moved}")
            else:
                # print("Doing single scaled movement")
                scaled_movement = amt_to_move_mm * direction_step_sizes[direction]
                movement_command += f" {direction.replace('d','').upper()}{scaled_movement}"
                amts_to_move.append(amt_to_move_mm)

        if not move_in_increments:
            movement_command += " F100000"
            print("\tSingle move --- ",  # "move:", amts_to_move,
                  "; CMD:", movement_command,
                  "; delay", measurement_delay)
            if move_motors:
                s.write(movement_command.encode('utf-8') + '\n'.encode('utf-8'))
                grbl_out = s.readline()

        # Wait for motion to stop and delay before measurement
        if move_motors:
            print("\t...Wait for move to finish...")
            wait_command = "G4 P0"  # "Dwell" for 0 s. This cmd delays the rest of the code until motors finish moving
            s.write(wait_command.encode('utf-8') + '\n'.encode('utf-8'))
            grbl_out = s.readline()  # This only runs once the motors finish moving.

            print("\tFinished moving... Delaying", measurement_delay, "s...")
            time.sleep(measurement_delay)  # Delay for the amount of specified time
            print("\tFinished delaying.")

        # Send a trigger for a measurement
        if send_external_trigger:
            print("\tSending external trigger")  # Takes about 2-5 ms for the pulse to go
            s.write(trigger_cmd_hi)
            s.readline()
            s.write(trigger_cmd_lo)
            s.readline()
            print("\tSleep for 1 ms after trigger")
            time.sleep(0.001)  # Wait 1 ms for trigger

        # Make the measurement
        if measure_probe:
            print("\tMaking measurement")
            thm.make_measurement(**params)
            meas = thm.last_reading
            measurements = list(meas.values())
            Bx = np.array(measurements[0])*10000
            By = np.array(measurements[1])*10000
            Bz = np.array(measurements[2])*10000
            Bmod = np.sqrt(Bx**2 + By**2 + Bz**2)

            print("\t ---> Measurement:", Bx, By, Bz, Bmod)
            string_to_write = ",".join(
                [str(command_num),
                 str(row["dx"]),
                 str(row["dy"]),
                 str(row["dz"]),
                 str(Bx[0]),
                 str(By[0]),
                 str(Bz[0]),
                 str(Bmod[0]),
                 str(row["x"]),
                 str(row["y"]),
                 str(row["z"]),
                 str(send_external_trigger),
                 "\n"
                 ])
            with open(output_filename, "a") as f:
                f.write(string_to_write)

    if measure_probe:
        thm.close()

    # Close connections
    if move_motors or send_external_trigger:
        s.close()

    print("Finished")
