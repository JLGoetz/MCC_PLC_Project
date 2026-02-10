from pylogix import PLC
from dotenv import load_dotenv
import time
import os
import threading
import sys


#Create done variable to control the monitoring thread
done = False

#Load Environment Variables and set PLC IP address
load_dotenv()
PLC_IP = os.getenv('UNIT_7')
print(f"{PLC_IP}")
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
def monitor_plc(stop_event):
    global initial_connection
    global counter
    global tags_to_monitor
    global tag_values

    print(f"Background montioring initialized.")
    #Use context manager to ensure proper connection handling
    while not stop_event.is_set():
        with PLC() as comm:
            comm.IPAddress = '10.22.128.92'
            #print(f"Connected to PLC at IP: {comm.IPAddress}")
            ret = comm.GetTagList()
            '''
            # Check for any errors in retrieving the list
            if ret.Status == 'Success':
                # Iterate over the list of tags and print their names
                for tag in ret.Value:
                    print(tag.TagName)
            else:
                print(f"Error retrieving tag list: {ret.Status}")
            '''
            #Read tags that need to be monitored
            for item in tags_to_monitor:
                #print(f"{item}")
                t = comm.Read(item)
                if initial_connection == True:
                    tag_values[item] = t.Value
                else:
                    tag_values.update({item: t.Value})
            #Set initial connection to false after first read 
            initial_connection = False
            #Increment counter and print tag values
            counter += 1
            #print(f"Counter: {counter}")
            #print(tag_values)

            #Pause monitoring thread for 1 second before next read
            time.sleep(1)

    print(f"Background process stopped.")

def show_menu():
    """Display Menu Options"""
    print(f"\n" + "="*40)
    print(f"    Simple Menu Program")
    print(f"="*40)
    print(f"1.  Get Current Tag Values")
    print(f"2.  Reset Tags")
    print(f"3.  Exit")
    print("="*40)

def main():
    stop_event = threading.Event()

    #Start background thread
    background_thread = threading.Thread(target=monitor_plc, args=(stop_event,), daemon=True) 
    #daemon shuts down thread when program stops
    background_thread.start()

    print("Program started. A background thread can be controlled via menu.")

    while True:
        show_menu()

        try:
            choice = input("Enter your choice (1-3): ").strip()
        except KeyboardInterrupt:
            print(f"\nInterrupted by user. Exiting...")
            stop_event.set()
            background_thread.join(timeout=1.0)
            sys.exit(0)

        if choice == "1":
            if background_thread is not None and background_thread.is_alive():
                print("→ Background thread is already running.")
                print(tag_values)
            else:
                stop_event.clear()  # reset event
                background_thread = threading.Thread(
                    target=monitor_plc,
                    args=(stop_event,),
                    daemon=True
                )
                background_thread.start()
                print("→ Background thread started.")

        elif choice == "2":
            if background_thread is None or not background_thread.is_alive():
                print("→ No background thread is running.")
            else:
                stop_event.set()
                background_thread.join(timeout=1.5)  # give it a moment to finish
                print("→ Background thread stopped.")
                background_thread = None  # allow restart

        elif choice == "3":
            print("\nShutting down...")
            if background_thread is not None and background_thread.is_alive():
                stop_event.set()
                background_thread.join(timeout=1.0)
            print("Goodbye!")
            sys.exit(0)

        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")

        # Small pause so output doesn't feel too rushed
        time.sleep(0.5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\nProgram Termintated by User.")
