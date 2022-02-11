from neotimer import *
from statemachine import *
from machine import Pin

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


# Main Loop: Run the state machine here
while True:
    state_machine.run()