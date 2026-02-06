#Designed to work with data structures and tags found in Week1.acd

from pylogix import PLC
import time

with PLC() as comm:
    comm.IPAddress = '10.22.128.92'

    ret = comm.GetTagList()
    
    # Check for any errors in retrieving the list
    if ret.Status == 'Success':
        # Iterate over the list of tags and print their names
        for tag in ret.Value:
            print(tag.TagName)
    else:
        print(f"Error retrieving tag list: {ret.Status}")
    
    #Read value of a single tag
    t = comm.Read('Program:MainProgram.Red_Pct') # Replace with your tag name

    # Print the results
    print(f"Tag Name: {t.TagName}")
    print(f"Tag Value: {t.Value}")
    print(f"Status: {t.Status}")

    # Reset all and read Tag for 10 seconds
    reset = input("Would you like to reset the timers? (y/n):")
    if reset == 'y':
        b = comm.Write('Program:MainProgram.Reset_All', True)
        time.sleep(2)
        b = comm.Write('Program:MainProgram.Reset_All', False)
        print(f"System Reset.")

    s = comm.Write('Program:MainProgram.Test_Tag', 12345)
    x=0
    while x < 11:
        t = comm.Read('Program:MainProgram.Red_Pct')
        print(f"Tag Name: {t.TagName}, Value: {t.Value}")
        x += 1
        time.sleep(1)

    #Read value of a single tag
    q = comm.Read('Program:MainProgram.Test_Tag') # Replace with your tag name

    # Print the results
    print(f"Tag Name: {q.TagName}")
    print(f"Tag Value: {q.Value}")
    print(f"Status: {q.Status}")


    #Write to an existing tag
    s = comm.Write('Program:MainProgram.Test_Tag', 12345)

    # Print the results
    print(f"Tag Name: {s.TagName}")
    print(f"Tag Value: {s.Value}")
    print(f"Status: {s.Status}")

