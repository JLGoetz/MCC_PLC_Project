import os
import sys
import time
import threading
from pylogix import PLC
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

class PLCController:
    def __init__(self, ip_address):
        # Sanitize IP string (removes whitespace and quotes)
        self.ip_address = ip_address.strip().replace('"', '').replace("'", "") if ip_address else None
        self.tag_values = {}
        self.lock = threading.Lock() 

    def is_valid(self):
        return self.ip_address is not None

    def read_batch(self, tags):
        if not self.ip_address: return
        with PLC() as comm:
            comm.IPAddress = self.ip_address
            comm.Timeout = 2000 # 2 second timeout
            for tag in tags:
                ret = comm.Read(tag)
                if ret.Status == 'Success':
                    with self.lock:
                        self.tag_values[tag] = ret.Value
        return self.tag_values

    def write_tag(self, tag, value):
        if not self.ip_address: return False
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

# Map display names to .env keys
plc_map = {
    "Unit 7": os.getenv('UNIT_7'),
    "Unit 8": os.getenv('UNIT_8')
}

# Initialize valid controllers
controllers = {}
for name, ip in plc_map.items():
    c = PLCController(ip)
    if c.is_valid():
        controllers[name] = c
    else:
        print(f"Warning: Configuration for {name} missing or invalid.")

def monitor_worker(name, controller, stop_event):
    """Specific thread loop for each PLC."""
    print(f"[System] Started monitoring {name} at {controller.ip_address}")
    while not stop_event.is_set():
        controller.read_batch(tags_to_monitor)
        time.sleep(1)
    print(f"[System] Stopped monitoring {name}")

def show_menu():
    print(f"\n" + "="*45)
    print(f"      MULTI-PLC CONTROL CONSOLE")
    print(f"      Connected Units: {', '.join(controllers.keys())}")
    print(f"="*45)
    print(f"1.  View All Tag Values")
    print(f"2.  Reset a Specific Unit (Pulse Reset_PB)")
    print(f"3.  Exit")
    print("="*45)

def main():
    if not controllers:
        print("No valid PLCs configured. Check your .env file.")
        return

    stop_event = threading.Event()
    threads = []

    # Launch one thread per PLC
    for name, ctrl in controllers.items():
        t = threading.Thread(target=monitor_worker, args=(name, ctrl, stop_event), daemon=True)
        t.start()
        threads.append(t)

    while True:
        show_menu()
        choice = input("Select Option (1-3): ").strip()

        if choice == "1":
            print("\n" + "-"*45)
            for name, ctrl in controllers.items():
                print(f"--- {name} ({ctrl.ip_address}) ---")
                with ctrl.lock:
                    if not ctrl.tag_values:
                        print("    [Connecting/No data yet...]")
                    for tag, val in ctrl.tag_values.items():
                        print(f"    {tag.split('.')[-1]:<15}: {val}")
                print("-"*45)

        elif choice == "2":
            print("\nWhich unit would you like to reset?")
            unit_names = list(controllers.keys())
            for i, name in enumerate(unit_names, 1):
                print(f"{i}. {name}")
            
            try:
                idx = int(input("Select Unit #: ")) - 1
                target_name = unit_names[idx]
                target_ctrl = controllers[target_name]
                
                print(f"→ Pulsing Reset on {target_name}...")
                if target_ctrl.write_tag('Program:MainProgram.Reset_PB', True):
                    time.sleep(0.5)
                    target_ctrl.write_tag('Program:MainProgram.Reset_PB', False)
                    print("→ Pulse complete.")
                else:
                    print("→ Write failed (Check connection).")
            except (ValueError, IndexError):
                print("Invalid selection.")

        elif choice == "3":
            print("\nShutting down all monitors...")
            stop_event.set()
            for t in threads:
                t.join(timeout=1.0)
            print("Goodbye!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)