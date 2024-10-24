import os
import serial
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import csv
from datetime import datetime


def get_port():
    '''
    Function to get port for flow sensor.
    '''
    cmd = "ls /dev/tty.usbserial* > port.txt"
    os.system(cmd)
    
    with open('port.txt', 'r') as file:
        lines = file.readlines()

    if len(lines) == 1:
        var = lines[0].strip()
        
        return var
    
    elif len(lines) == 0:
        print("Error: The port file is empty.")
    else:
        print("Error: The port file contain more than one port")

def initFlowMeter():
    '''
    This part is copy-paste from Michael's python code.\n
    It is used to setup the measurement units and choose the lookup table for DMF
    that has been save in the flow sensor already.
    '''
    cmdlist = [b'cels 0\n',
               b'celd 0 2\n',# 0 2  will call the 2nd lookup table
               b'MRU state.flow_data[0].scale.decimals\n',
               b'MWU state.flow_data[0].scale.decimals 0\n',
               b'MRU state.flow_data[0].scale.decimals\n',
               b'MRSTR state.flow_data[0].scale.units\n',
               b'MWSTR state.flow_data[0].scale.units nL/min\n',
               b'MRSTR state.flow_data[0].scale.units\n',
               b' MRSTR state.flow_data[0].calibration_table.description\n',
               b'sens\n']

    for cmd in cmdlist:
        serfm.write(cmd)
        time.sleep(0.100) # sleep 100 ms
        x = serfm.read_all()
        print(x)

def readFlow():
    '''
    Function to read flow
    '''
    serfm.write(b'sens\n')
    time.sleep(0.125)
    x = serfm.read_all()
    # print(x)
    try:
        flow = int(str(x).split(':')[1].split('\\')[0])
    except (IndexError, ValueError):
        flow = 0  # Default value if parsing fails

    return flow

def update(frame):
    '''
    Function to update the plot
    '''
    global running, start_time
    if running:
        if start_time is None:  # Set the start time on the first update
            start_time = time.time()

        flow = readFlow()
        current_time = time.time()
        
        # Append new values
        elapsed_time = current_time - start_time  # Calculate elapsed time in seconds
        time_values.append(elapsed_time)  # Keep it in seconds
        flow_values.append(flow)

        # Limit x and y data to the last 100 points for better visualization
        if len(time_values) > 100:
            time_values.pop(0)
            flow_values.pop(0)

        # Clear and plot
        ax.clear()
        ax.plot(time_values, flow_values, label='Flow')
        ax.set_xlabel('Time (sec)')  # Change label to seconds
        ax.set_ylabel('Flow Rate (nL/min)')
        # ax.set_title('Flow Rate Over Time')
        ax.legend()
        ax.grid()

def stop(event):
    global running
    running = False  # Set the flag to stop data collection

def resume(event):
    global running
    running = True  # Set the flag to resume data collection

def save(event):
    filename = datetime.now().strftime("flow_data_%Y%m%d_%H%M%S.csv")
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Time (s)', 'Flow Rate (nL/min)'])
        for elapsed_time, flow in zip(time_values, flow_values):
            writer.writerow([f"{elapsed_time:.3f}", flow])  # Use elapsed_time directly
    print(f"Data saved to {filename}")



# Get port for the flow sensor
port = get_port()

# Create a serial object
serfm = serial.Serial(port,115200,timeout=1)

# Initiate the flow meter
initFlowMeter()

# Lists to store time and flow values for plotting
time_values = []
flow_values = []
running = True  # Flag to control the animation

# Initialize start_time
start_time = None  

# Set up the figure and axis
fig, ax = plt.subplots()
ani = animation.FuncAnimation(fig, update, interval=100, cache_frame_data=False)  # Update every 100ms

# Add buttons to the top right corner
stop_ax = plt.axes([0.8, 0.9, 0.1, 0.075])
stop_button = Button(stop_ax, 'Stop')
stop_button.on_clicked(stop)

resume_ax = plt.axes([0.7, 0.9, 0.1, 0.075])
resume_button = Button(resume_ax, 'Resume')
resume_button.on_clicked(resume)

save_ax = plt.axes([0.6, 0.9, 0.1, 0.075])
save_button = Button(save_ax, 'Save')
save_button.on_clicked(save)

plt.show()

# Cleanup serial connection
serfm.close()
print("Serial port closed.")