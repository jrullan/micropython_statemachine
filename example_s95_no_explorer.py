DEBUG_MODE = True

import gc
print("After gc",gc.mem_free())

from neotimer import *                    #<---- 3,088 bytes
print("After Neotimer",gc.mem_free())

from statemachine import *                #<---- 3,616 bytes
print("After State Machine",gc.mem_free())

from machine import Pin
import time
print("After machine, pin and time",gc.mem_free())

# Needs custom UF2 from Pimoroni
import picoexplorer as explorer
print("After Importing Pico Explorer",gc.mem_free())


state_machine = StateMachine()           #<--- 96 bytes
print("After 1 instance of StateMachine",gc.mem_free())

debouncing_timer = Neotimer(200)         #<--- 64 bytes
print("After 1 instance of Neotimer",gc.mem_free())


blinker = Neotimer(250)
transition_timer = Neotimer(1000)

led = Pin(25,Pin.OUT)
led.off()

BUTTON_A = Pin(12,Pin.IN,Pin.PULL_UP)
BUTTON_B = Pin(13,Pin.IN,Pin.PULL_UP)
BUTTON_X = Pin(14,Pin.IN,Pin.PULL_UP)
BUTTON_Y = Pin(15,Pin.IN,Pin.PULL_UP)


print("After Pico Explorer",gc.mem_free())    #<---- 115,392 bytes


# Use to print messages to LCD and optionally (when DEBUG_MODE == True)
# to the shell
def notify(string):
    if DEBUG_MODE:
        print(string, gc.mem_free())
    
def blink():
    if blinker.repeat_execution():
        led.toggle()

def is_pressed(pin):
    return not pin.value()

print("Before creating all logic and states",gc.mem_free())     #<---- 1952 bytes of logic and states

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
    
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_X)):
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
    
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_X)):
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

def stopping_logic():
    if state_machine.execute_once:
        notify("Stopping")
        transition_timer.start()
 
    blink()
    
    if transition_timer.finished():
        state_machine.force_transition_to(stopped)

def stopped_logic():
    if state_machine.execute_once:
        notify("Stopped")
    
    led.off()
    
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_A)):
        state_machine.force_transition_to(resetting)

# def aborted_logic():
#     if state_machine.execute_once:
#         notify("Aborted")
# 
#     led.off()

print("After states logic",gc.mem_free())

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
stopping = state_machine.add_state(stopping_logic)
stopped = state_machine.add_state(stopped_logic)
# aborted = state_machine.add_state(aborted_logic)


#============================================================
# State Transitions Functions (optional)
#============================================================
def next_transition():
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_A)) and transition_timer.finished():  #<---- Advance condition
        return True
    else:
        return False

def stop_transition():
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_B)):  #<---- Stop condition
        return True
    else:
        return False
    
#============================================================
# Attach transitions to states (optional)
#============================================================
# Attach transitions to all states
for state in state_machine.state_list:
    state.attach_transition(stop_transition, stopping)

idle.attach_transition(next_transition,starting)
execute.attach_transition(next_transition,completing)
completed.attach_transition(next_transition,resetting)

print("After creating all logic and states",gc.mem_free())

gc.collect()

# Main Loop: Run the state machine here
while True:
    
    # Determine if machine will run normally or in jog mode
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_Y)):
        state_machine.jog_mode = True if state_machine.jog_mode == False else False
        if state_machine.jog_mode:
            print("Machine in Jog Mode")
        else:
            print("Machine in Run Mode")

    if state_machine.jog_mode:    
        if debouncing_timer.debounce_signal(is_pressed(BUTTON_X)):
            state_machine.jog()
    
    # Run state machine state's logics
    state_machine.run()