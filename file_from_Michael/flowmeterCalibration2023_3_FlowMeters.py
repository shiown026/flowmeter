#!/usr/bin/python3


import serial
import time
import sys,os

# Instructions:
# Use the provided software [calibration_editor_20170331.exe] to communicate with the flow meter.
# Use the software to identify the correct com port(s)
# Use the software to load the desired table to use when measuring.  Actually it seems the script will spedify this below
       # This line(s) -> [b'celd 0 2\n',# 0 2  will call the 2nd lookup table]
# Modify this script to look at the correct com port(s) and set the export file name (at the bottom of this script)

serfm = serial.Serial('com3',115200,timeout=1)    # make sure this is the table with DMF (I initialize it with water table for raw readings)
serfm2 = serial.Serial('com4',115200,timeout=1)   # xxxThis one is initialized with methanol.
serfm3 = serial.Serial('com5',115200,timeout=1)   # xxxThis one is initialized with methanol.

# ser = serial.Serial('/dev/ttyACM0',1000000,timeout=0)
# ser.write(b'?\n')


# time.sleep(0.005)

# x=ser.read_all()
# print(x)

def initFlowMeter():
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
    # cmd =b'cels 0\n'
    for cmd in cmdlist:
        serfm.write(cmd)
        time.sleep(0.100)
        x = serfm.read_all()
        print(x)
    # cmdlist = [b'cels 0\n',
    #            b'celd 0 3\n', # 0 2  will call the 2nd lookup table
    #            b'MRU state.flow_data[0].scale.decimals\n',
    #            b'MWU state.flow_data[0].scale.decimals 0\n',
    #            b'MRU state.flow_data[0].scale.decimals\n',
    #            b'MRSTR state.flow_data[0].scale.units\n',
    #            b'MWSTR state.flow_data[0].scale.units nL/min\n',
    #            b'MRSTR state.flow_data[0].scale.units\n',
    #            b' MRSTR state.flow_data[0].calibration_table.description\n',
    #            b'sens\n']
    for cmd in cmdlist:
        serfm2.write(cmd)
        time.sleep(0.100)
        x2 = serfm2.read_all()
        print(x2)

    for cmd in cmdlist:
        serfm3.write(cmd)
        time.sleep(0.100)
        x3 = serfm3.read_all()
        print(x3)


def readFlow():
    serfm.write(b'sens\n')
    serfm2.write(b'sens\n')
    serfm3.write(b'sens\n')
    time.sleep(0.123)
    x = serfm.read_all()
    x2 = serfm2.read_all()
    x3 = serfm3.read_all()
    #print(x)
    flow=int(str(x).split(':')[1].split('\\')[0])
    flow2=int(str(x2).split(':')[1].split('\\')[0])
    flow3=int(str(x3).split(':')[1].split('\\')[0])
    # flow2=0

    # print("Flow:" +str(flow)+"," +str(flow2))
    print("Flow: " + str(flow) + '  '+str(flow2) + '  '+str(flow3))
    return flow, flow2, flow3
    # return flow
    # return flow2



initFlowMeter()

while(1):
    t=time.time()
    x,x2,x3 = readFlow()
    # x=readFlow()
    # cmd = "echo "+str(t)+"," + str(x)+"," + str(x2) + " >> flowlog_mass_2020
    # 1211__1301_10_mbar.txt"   # This is the log file name
    cmd = "echo "+str(t)+"," + str(x) + "," + str(x2)+ "," + str(x3) + " >> flowlog_mass_20240703_Triple_flom_meter_meas_01.csv"   # This is the log file name
    os.system(cmd)
    
