from neotimer import *
from statemachine import *
from machine import Pin
# Needs custom UF2 from Pimoroni
import picoexplorer as explorer

state_machine = StateMachine()
myTimer = Neotimer(1000)

#============================================================
# States Logic Functions
#============================================================
def state1_logic():
    if state_machine.execute_once:
        print("Machine in State 1")
        
    pass

#============================================================
# Add states to machine (Also create state objects)
#============================================================
state1 = state_machine.add_state(state1_logic)

#============================================================
# State Transitions Functions (optional)
#============================================================


#============================================================
# Add transitions to states (optional)
#============================================================


# Main Loop: Run the state machine here
while True:
    state_machine.run()