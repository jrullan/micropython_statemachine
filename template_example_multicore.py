from neotimer import *
from statemachine import *
from machine import Pin, UART
import time, gc, _thread

state_machine = StateMachine()
myTimer = Neotimer(1000)
led = Pin(25,Pin.OUT)

#============================================================
# States Logic Functions
#============================================================
def state0_logic():
    # Referenced global variables
    # ----> Here <----
    
    if state_machine.execute_once:
        # ----> Code that executes just once during state <----
        # ----> Here <----
        print("Machine in State 0")
        myTimer.start()

    # Code that executes continously during state
    # ----> Here <----
    led.off()
    

def state1_logic():
    # Referenced global variables
    # ----> Here <----
    
    if state_machine.execute_once:
        # ----> Code that executes just once during state <----
        # ----> Here <----
        print("Machine in State 1")
        myTimer.start()

    # Code that executes continously during state
    # ----> Here <----   
    led.on()

#============================================================
# Add states to machine (Also create state objects)
#============================================================
# Create States
# ----> Here <----
state0 = state_machine.add_state(state0_logic)
state1 = state_machine.add_state(state1_logic)

#============================================================
# State Transitions Functions (optional)
#============================================================
# Create Transition Functions
# ----> Here <----
def delay_transition():
    if myTimer.finished():
        return True
    else:
        return False

#============================================================
# Attach transitions to states (optional)
#============================================================
state0.attach_transition(delay_transition, state1)
state1.attach_transition(delay_transition, state0)



def main_loop():
    #global variable
    global free_memory_threshold

    # Manually invoke garbage collection
    # It might be required in both cores, but
    # start using it on the fastest looping core.

    if gc.mem_free() < free_memory_threshold:
        #lock.acquire()
        gc.collect()
        #lock.release()
        
    pass # Do something here

#------------------------------------------------------
# Run state machine code in second core
def state_machine_logic():
    while True:
        state_machine.run()

# Start state_machine_logic() on Core 1
_thread.start_new_thread(state_machine_logic, ())
#------------------------------------------------------


# Determine how much memory is free before starting
# main loop in Core 0. This will be used as threshold
# to determine if we should invoke gc.collect()
gc.collect()
free_memory_threshold = gc.mem_free()
print("Free memory",free_memory_threshold)

# Main Loop:
while True:
    main_loop()