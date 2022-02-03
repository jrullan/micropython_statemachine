from neotimer import *
from statemachine import *
from machine import Pin
import time
# Needs custom UF2 from Pimoroni
import picoexplorer as explorer

state_machine = StateMachine()
debouncing_timer = Neotimer(200)
blinker = Neotimer(250)

led = Pin(25,Pin.OUT)
led.off()

# Pimoroni Explorer Initialization
width = explorer.get_width()
height = explorer.get_height()
display_buffer = bytearray(width * height * 2)  # 2-bytes per pixel (RGB565)
explorer.init(display_buffer)
explorer.clear()
time.sleep(0.01) #<---- Needed otherwise crashes
explorer.update()

#============================================================
# States Logic Functions
#============================================================
def state0_logic():
    if state_machine.execute_once:
        print("Machine in State 0: System Initialization")

    state_machine.transition_to(state1)


def state1_logic():
    if state_machine.execute_once:
        print("Machine in State 1: Blinking Led")

    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_A)):
        state_machine.transition_to(state2)

    if blinker.repeat_execution():
        led.toggle()


def state2_logic():
    if state_machine.execute_once:
        print("Machine in State 2: Led Off")
        led.off()
        
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_A)):
        state_machine.transition_to(state1)
    
        
#============================================================
# Add states to machine (Also create state objects)
#============================================================
state0 = state_machine.add_state(state0_logic)
state1 = state_machine.add_state(state1_logic)
state2 = state_machine.add_state(state2_logic)


#============================================================
# State Transitions Functions (optional)
#============================================================
# This is a transition from any state to state0 whenever the
# B button is pressed.
def transition_from_any_to_0():
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_B)):
        return True
    else:
        return False


#============================================================
# Add transitions to states (optional)
#============================================================
# Attach a transition to state0 to all states.
# Useful for an abnormal condition that requires a transition
# from any state. 
for state in state_machine.state_list:
    state.add_transition(transition_from_any_to_0, state0)



# Main Loop: Run the state machine here
while True:
    state_machine.run()