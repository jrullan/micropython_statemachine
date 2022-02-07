from neotimer import *
from statemachine import *
from machine import Pin
import time
# Needs custom UF2 from Pimoroni
import picoexplorer as explorer

state_machine = StateMachine()
debouncing_timer = Neotimer(200)
blinker = Neotimer(250)
transition_timer = Neotimer(1000)

led = Pin(25,Pin.OUT)
led.off()

# Pimoroni Explorer Initialization
width = explorer.get_width()
height = explorer.get_height()
display_buffer = bytearray(width * height * 2)  # 2-bytes per pixel (RGB565)
explorer.init(display_buffer)

color_black = explorer.create_pen(0,0,0)
color_white = explorer.create_pen(255,255,255)

explorer.set_pen(color_black)
explorer.clear()
time.sleep(0.01) #<---- Needed otherwise crashes
explorer.update()

#============================================================
# States Logic Functions
#============================================================
def state0_logic():
    if state_machine.execute_once:
        print("Machine in State 0: System Initialization")
        update_text("State 0")
        explorer.update()
        transition_timer.start()

    if transition_timer.finished():
        state_machine.force_transition_to(state1)


def state1_logic():
    if state_machine.execute_once:
        print("Machine in State 1: Blinking Led")
        update_text("State 1")

    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_A)):
        state_machine.force_transition_to(state2)

    if blinker.repeat_execution():
        led.toggle()


def state2_logic():
    if state_machine.execute_once:
        print("Machine in State 2: Led Off")
        update_text("State 2")
        led.off()
        
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_A)):
        state_machine.force_transition_to(state1)
    
        
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
# Attach transitions to states (optional)
#============================================================
# Attach transitions to all states
for state in state_machine.state_list:
    state.attach_transition(transition_from_any_to_0, state0)


def update_text(string):
    explorer.set_clip(5,10,75,15)
    explorer.set_pen(color_black)
    explorer.clear()
    explorer.set_pen(color_white)
    explorer.text(string,5,10,100)


# Main Loop: Run the state machine here
while True:
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_Y)):
        state_machine.jog_mode = True if state_machine.jog_mode == False else False
        if state_machine.jog_mode:
            print("Machine in Jog Mode")
        else:
            print("Machine in Run Mode")

    state_machine.run()

    if state_machine.jog_mode:    
        if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_X)):
            state_machine.jog()
    
    explorer.update()  