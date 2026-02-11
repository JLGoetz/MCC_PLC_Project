from pylogix import PLC
from dotenv import load_dotenv
import time
import os
import threading
import sys


# Load Environment Variables
load_dotenv()
#PLC_IP = os.getenv('UNIT_7', '10.22.128.92') # Fallback to hardcoded if .env missing
PLC_IP ='10.22.128.92'

class PLCController:
    def __init__(self, ip_address, slot=0):
        self.ip_address = ip_address.strip().replace('"', '').replace("'", "") if ip_address else None
        self.slot = slot # Default for most Allen-Bradley PLCs
        self.tag_values = {}
        self.lock = threading.Lock() # Ensures thread-safe dictionary updates

    def read_batch(self, tags):
        if not self.ip_address: return

        """Reads a list of tags and updates the local dictionary."""
        with PLC() as comm:
            comm.IPAddress = self.ip_address
            comm.ProcessorSlot = self.slot # Explicitly set the slot
            comm.SocketTimeout = 5000           # Increase timeout to 5 seconds
            
            for tag in tags:
                ret = comm.Read(tag)
                if ret.Status == 'Success':
                    with self.lock:
                        self.tag_values[tag] = ret.Value
                else:
                    # This will help us see if it's a specific tag or a connection loss
                    print(f"\n[Error] {self.ip_address} failed on {tag}: {ret.Status}")
                    if "timed out" in ret.Status.lower():
                        break # Stop trying other tags if the first one timed out
        return self.tag_values

    def write_tag(self, tag, value):
        """Writes a value to a specific tag."""
        with PLC() as comm:
            comm.IPAddress = self.ip_address
            ret = comm.Write(tag, value)
            return ret.Status == 'Success'

# --- Configuration ---
tags_to_monitor = [
    'Program:MainProgram.Red_Light', 
    'Program:MainProgram.Green_Light', 
    'Program:MainProgram.Yellow_Light', 
    'Program:MainProgram.Red_Pct', 
    'Program:MainProgram.Green_Pct', 
    'Program:MainProgram.Yellow_Pct', 
    'Program:MainProgram.Cycle_Timer.ACC', 
    'Program:MainProgram.Traffc_Timer.ACC', 
    'Program:MainProgram.Reset_PB'
]

# Initialize Controller
plc = PLCController(PLC_IP, 1)

def monitor_worker(stop_event):
    """Background loop for continuous monitoring."""
    print(f"\n[System] Background monitoring started for {plc.ip_address}")
    while not stop_event.is_set():
        plc.read_batch(tags_to_monitor)
        time.sleep(1)
    print("\n[System] Background process stopped.")

def show_menu():
    print(f"\n" + "="*40)
    print(f"      PLC Management Console")
    print(f"      Target: {PLC_IP}")
    print(f"="*40)
    print(f"1.  View Current Tag Values")
    print(f"2.  Pulse Reset Push Button (Reset_PB)")
    print(f"3.  Exit")
    print("="*40)

def main():
    stop_event = threading.Event()
    bg_thread = threading.Thread(target=monitor_worker, args=(stop_event,), daemon=True)
    bg_thread.start()

    while True:
        show_menu()
        choice = input("Enter selection (1-3): ").strip()

        if choice == "1":
            print("\n--- Current PLC Data ---")
            with plc.lock:
                if not plc.tag_values:
                    print("No data received yet...")
                for tag, val in plc.tag_values.items():
                    print(f"{tag.split('.')[-1]:<15}: {val}")

        elif choice == "2":
            print("\n→ Sending Reset Pulse...")
            # Pulse Logic: True then False
            if plc.write_tag('Program:MainProgram.Reset_PB', True):
                time.sleep(0.5)
                plc.write_tag('Program:MainProgram.Reset_PB', False)
                print("→ Reset_PB pulsed successfully.")
            else:
                print("→ Failed to communicate with PLC for Reset.")

        elif choice == "3":
            print("\nShutting down...")
            stop_event.set()
            bg_thread.join(timeout=1.0)
            print("Goodbye!")
            break
        else:
            print("\nInvalid selection.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess terminated by user.")
        sys.exit(0)