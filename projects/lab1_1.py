from pylogix import PLC
from dotenv import load_dotenv
import time
import os
import threading

#Create done variable to control the monitoring thread
done = False

#Load Environment Variables and set PLC IP address
load_dotenv()
PLC_IP = os.getenv('STATION1_IP')

print(f"Connecting to PLC at IP: {PLC_IP}")

#Create list of tags of interest to monitor
tags_to_monitor = ['Program:MainProgram.Red_Light', 'Program:MainProgram.Green_Light', 'Program:MainProgram.Yellow_Light', 'Program:MainProgram.Red_Pct', 'Program:MainProgram.Green_Pct', 'Program:MainProgram.Yellow_Pct', 'Program:MainProgram.Cycle_Timer.ACC', 'Program:MainProgram.Traffc_Timer.ACC']

#Create empty dictionary to store tag values
tag_values = {}

#Set init variable to indicate initial connection to PLC
initial_connection = True   

#Define counter
counter = 0

#define a function to monitor the PLC tag in a separate thread
def monitor_plc():
    #Use context manager to ensure proper connection handling
    with PLC() as comm:
        comm.IPAddress = PLC_IP
        #Create loop to continuously read tags until done is set to True
        while not done:
            #Read tags that need to be monitored
            for item in tags_to_monitor:
                t = comm.Read(item)
                if initial_connection == True:
                    tag_values[item] = t.Value
                else:
                    tag_values.update({item: t.Value})
            #Set initial connection to false after first read 
            initial_connection = False
            #Increment counter and print tag values
            counter += 1
            print(f"Counter: {counter}")
            print(tag_values)

            #Pause monitoring thread for 1 second before next read
            time.sleep(1)

#start the monitoring thread
threading.Thread(target=monitor_plc, daemon=True).start()  #create thread by passing object to the thread.  .start() inisializes it upon creation

#Main thread can perform other tasks here, for example, writing to a tag
#Enter is used to end the program and stop the monitoring thread
input("Press enter to quit")
done = True



