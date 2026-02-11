from pylogix import PLC
import os
from dotenv import load_dotenv

load_dotenv()
#PLC_IP = os.getenv('UNIT_7', '10.22.128.92').strip().replace('"', '')
PLC_IP = '10.22.128.92'

def discover_plc_slot(ip):
    print(f"--- Initiating Auto-Discovery for {ip} ---")
    
    with PLC() as comm:
        comm.IPAddress = ip
        # A short timeout is fine for discovery
        comm.SocketTimeout = 2000 
        
        # Step 1: Identify the device at the IP address
        device = comm.GetDeviceProperties()
        if device.Status != 'Success':
            print(f"[Error] Could not reach {ip}. Status: {device.Status}")
            return None
        
        print(f"Connected to: {device.Value.ProductName}")
        print(f"Revision: {device.Value.Revision}")

        # Step 2: Scan the backplane for a Controller module
        # This returns all modules in the rack/chassis
        print("Scanning backplane for Processor...")
        modules = comm.GetModuleProperties()
        
        if modules.Status == 'Success':
            print(modules)
            for module in modules.Value:
                # We look for "Logix" in the product name (ControlLogix, CompactLogix)
                if 'Logix' in module.ProductName or '55' in module.ProductName or '53' in module.ProductName:
                    print(f"\n>>> SUCCESS: Found Processor '{module.ProductName}' in Slot {module.Slot}")
                    return module.Slot
            
            print("\n[Warning] Reached device, but no Logix processor was identified in the module list.")
        else:
            print(f"[Error] Could not retrieve module list: {modules.Status}")
            
    return None

if __name__ == "__main__":
    found_slot = discover_plc_slot(PLC_IP)
    
    if found_slot is not None:
        print(f"\nUse this configuration in your main script:")
        print(f"IP: {PLC_IP}")
        print(f"Slot: {found_slot}")
    else:
        print("\nDiscovery failed. Check physical connection or try manual Slot 0 or 1.")