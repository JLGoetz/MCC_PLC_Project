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
        print(dir(device.Value))

        devices = comm.Discover()
        for device in devices.Value:
            devices = comm.Discover()
    for device in devices.Value:
            if '1769-L27ERM-QxC1B/A' in device.ProductName:
                print(device.ProductName, device.Revision, device.IPAddress)

            
    return None

if __name__ == "__main__":
    found_slot = discover_plc_slot(PLC_IP)
    
    if found_slot is not None:
        print(f"\nUse this configuration in your main script:")
        print(f"IP: {PLC_IP}")
        print(f"Slot: {found_slot}")
    else:
        print("\nDiscovery failed. Check physical connection or try manual Slot 0 or 1.")