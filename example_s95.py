from neotimer import *
from statemachine import *
from machine import Pin
import time, gc
# Needs custom UF2 from Pimoroni
import picoexplorer as explorer

DEBUG_MODE = True

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


# Draw a string in the LCD
def update_text(string):
    #explorer.set_clip(5,10,150,15)
    explorer.set_pen(color_black)
    explorer.clear()
    explorer.set_pen(color_white)
    explorer.text(string,5,10,100)

# Use to print messages to LCD and optionally (when DEBUG_MODE == True)
# to the shell
def notify(string):
    if DEBUG_MODE:
        print(string, gc.mem_free())
    update_text(string)
    
def blink():
    if blinker.repeat_execution():
        led.toggle()

#============================================================
# States Logic Functions
#============================================================
def idle_logic():
    if state_machine.execute_once:
        notify("Idle")
        transition_timer.start()
    
    led.off()
        
def starting_logic():
    if state_machine.execute_once:
        notify("Starting")
        transition_timer.start()
    
    blink()
    
    if transition_timer.finished():
        state_machine.force_transition_to(execute)

def execute_logic():
    if state_machine.execute_once:
        notify("Execute")
        transition_timer.start()
    
    led.on()
    
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_X)):
        state_machine.force_transition_to(suspending)

def completing_logic():
    if state_machine.execute_once:
        notify("Completing")
        transition_timer.start()
    
    blink()
    
    if transition_timer.finished():
        state_machine.force_transition_to(completed)

def completed_logic():
    if state_machine.execute_once:
        notify("Completed")
        transition_timer.start()

    led.off()
    
def resetting_logic():
    if state_machine.execute_once:
        notify("Resetting")
        transition_timer.start()
    
    blink()
    
    if transition_timer.finished():
        state_machine.force_transition_to(idle)

def suspending_logic():
    if state_machine.execute_once:
        notify("Suspending")
        transition_timer.start()
    
    blink()
    
    if transition_timer.finished():
        state_machine.force_transition_to(suspended)

def suspended_logic():
    if state_machine.execute_once:
        notify("Suspended")

    led.off()
    
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_X)):
        state_machine.force_transition_to(unsuspending)

def unsuspending_logic():
    if state_machine.execute_once:
        notify("Un-suspending")
        transition_timer.start()
    
    blink()
    
    if transition_timer.finished():
        state_machine.force_transition_to(execute)

def held_logic():
    if state_machine.execute_once:
        notify("Held")
    
    led.off()

# def stopping_logic():
#     if state_machine.execute_once:
#         notify("Stopping")
#         transition_timer.start()
#     
#     blink()
#     
#     if transition_timer.finished():
#         state_machine.force_transition_to(stopped)

def stopped_logic():
    if state_machine.execute_once:
        notify("Stopped")
    
    #led.off()
    
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_A)):
        state_machine.force_transition_to(resetting)

def aborted_logic():
    if state_machine.execute_once:
        notify("Aborted")

    #led.off()

#============================================================
# Add states to machine (Also create state objects)
#============================================================
idle = state_machine.add_state(idle_logic)
starting = state_machine.add_state(starting_logic)
execute = state_machine.add_state(execute_logic)
completing = state_machine.add_state(completing_logic)
completed = state_machine.add_state(completed_logic)
resetting = state_machine.add_state(resetting_logic)
suspending = state_machine.add_state(suspending_logic)
suspended = state_machine.add_state(suspended_logic)
unsuspending = state_machine.add_state(unsuspending_logic)
held = state_machine.add_state(held_logic)
# stopping = state_machine.add_state(stopping_logic)
stopped = state_machine.add_state(stopped_logic)
aborted = state_machine.add_state(aborted_logic)


#============================================================
# State Transitions Functions (optional)
#============================================================
def next_transition():
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_A)) and transition_timer.finished():  #<---- Advance condition
        return True
    else:
        return False

def stop_transition():
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_B)):  #<---- Stop condition
        return True
    else:
        return False
    
#============================================================
# Attach transitions to states (optional)
#============================================================
# Attach transitions to all states
for state in state_machine.state_list:
    state.attach_transition(stop_transition, stopped)

idle.attach_transition(next_transition,starting)
execute.attach_transition(next_transition,completing)
completed.attach_transition(next_transition,resetting)


# Main Loop: Run the state machine here
while True:
    
    explorer.update()
    
    # Determine if machine will run normally or in jog mode
    if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_Y)):
        state_machine.jog_mode = True if state_machine.jog_mode == False else False
        if state_machine.jog_mode:
            print("Machine in Jog Mode")
        else:
            print("Machine in Run Mode")

    if state_machine.jog_mode:    
        if debouncing_timer.debounce_signal(explorer.is_pressed(explorer.BUTTON_X)):
            state_machine.jog()
    
    # Run state machine state's logics
    state_machine.run()