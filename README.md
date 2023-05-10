# prusa_plottemp.py - Plots temperature readings from a Prusa 3D printer.

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

## Installing dependencies
Some basic steps...

```bash
python3 -m venv env
source ./env/bin/activate
python3 -m pip install -r requirements.txt
```

## Usage
Run the script within your activated virtual environment and pass in the path to a 
text file containing temperature log lines.

`python3 ./prusa_plottemp.py <path/to/logfile>`