#!/usr/bin/env python3
"""
prusa_plottemp.py - Plots temperature readings from a Prusa 3D printer.

This is a hacky script for plotting temperature readings and thermal model
errors from a Prusa 3D printer. I wrote it to troubleshoot thermal anomalies
reported by my MK3S+.

Send the following commands to the printer over a serial connection to
log temperature data and thermal model errors during a print or PID calibration
run. Save the serial output from the printer to a file, then run this script to
plot temperature readings over time. For more info, see: 
https://help.prusa3d.com/article/thermal-model-calibration_382488

```gcode
M155 S1 C3 ; enable advanced temp and fan logging
D70 I1     ; enable temp model debug logging
```
Depends on matplotlib and tk.

Usage: 
    python3 prusa_plottemp.py <path/to/logfile>
"""

import sys
import re
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


temp_expr = re.compile(r'T:(?P<actual_temp>[\d\.]+) /(?P<target_temp>[\d\.]+) B:(?P<actual_bed>[\d\.]+) /(?P<target_bed>[\d\.]+) T0:(?P<tool0_temp>[\d\.]+) /(?P<tool0_target>[\d\.]+) @:(?P<power>[\d\.]+) B@:(?P<bed_power>[\d\.]+) P:(?P<p>[\d\.]+) A:(?P<ambient>[\d\.]+)') 
calibration_temp_expr = re.compile(r'T:(?P<actual_temp>[\d\.]+) @:(?P<power>[\d\.]+)')
err_expr = re.compile(r'TM: error \|(?P<err_diff>[-\.\d]+)\|>(?P<err_threshold>[-\.\d]+)')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 prusa_plottemp.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]
    print("Plotting temperature data from file: " + filename)

    actual_temps = []
    target_temps = []
    actual_beds = []
    target_beds = []
    powers = []
    bed_powers = []
    ambient_temps = []

    thermal_errors = []
    total_thermal_errors = 0

    with open(filename, "r") as f:
        lineno = 0
        last_err_pos = None
        for line in f:
            lineno += 1
            temp_line = temp_expr.match(line)
            if temp_line:
                actual_temps.append(float(temp_line.group("actual_temp")))
                target_temps.append(float(temp_line.group("target_temp")))
                actual_beds.append(float(temp_line.group("actual_bed")))
                target_beds.append(float(temp_line.group("target_bed")))
                powers.append(float(temp_line.group("power")) / 127.0 * 100.0)
                bed_powers.append(float(temp_line.group("bed_power")) / 127.0 * 100.0)
                ambient_temps.append(float(temp_line.group("ambient")))

            calibration_temp_line = calibration_temp_expr.match(line)
            if calibration_temp_line:
                actual_temps.append(float(calibration_temp_line.group("actual_temp")))
                powers.append(float(calibration_temp_line.group("power")) / 127.0 * 100.0)
                target_temps.append(0.0)
                actual_beds.append(0.0)
                target_beds.append(0.0)
                bed_powers.append(0.0)
                ambient_temps.append(0.0)
            
            err_line = err_expr.match(line)
            if err_line:
                pos = len(actual_temps)
                total_thermal_errors += 1
                if last_err_pos != pos:
                    thermal_errors.append(pos)
                    last_err_pos = pos

    print("Found " + str(len(actual_temps)) + " temperature data points")
    print("Power range: " + str(min(powers)) + " - " + str(max(powers)))
    print("Bed Power range: " + str(min(bed_powers)) + " - " + str(max(bed_powers)))
    print("Ambient range: " + str(min(ambient_temps)) + " - " + str(max(ambient_temps)))
    print("Extruder Actual range: " + str(min(actual_temps)) + " - " + str(max(actual_temps)))
    print("Bed Actual range: " + str(min(actual_beds)) + " - " + str(max(actual_beds)))
    print("Errors: " + str(len(thermal_errors)) + " - " + str(total_thermal_errors))
    
    x = np.linspace(0, len(actual_temps), len(actual_temps))
    
    mpl.use("TkAgg")
    fig, axis = plt.subplots(layout="constrained")

    axis.set_xlabel("Time (seconds)")
    axis.set_ylabel("Temperature (C)")
    axis.set_title("Temperature Data from " + filename)

    axis.plot(x, actual_temps, label="Extruder Actual")
    axis.plot(x, target_temps, label="Extruder Target")
    axis.plot(x, actual_beds, label="Bed Actual")
    axis.plot(x, target_beds, label="Bed Target")
    axis.plot(x, ambient_temps, label="Ambient")
    axis.vlines(thermal_errors, 0, max(actual_temps), colors="red", linestyles="dashed", label="Thermal Error")
    fig.legend(loc="outside center left")

    plt.show()
