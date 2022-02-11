DEBUG_MODE = True

import gc
from neotimer import *                    #<---- 3,088 bytes
from statemachine import *                #<---- 3,616 bytes
from pitches import *
from machine import Pin, PWM
import time

state_machine = StateMachine()           #<--- 96 bytes
debouncing_timer = Neotimer(200)         #<--- 64 bytes

blinker = Neotimer(75)
transition_timer = Neotimer(300)
player = Neotimer(150)

led = Pin(25,Pin.OUT)
led.off()

buzzer = machine.PWM(machine.Pin(18))  # set pin 18 as PWM OUTPUT

# Cytron onboard buttons
BUTTON_A = Pin(20,Pin.IN,Pin.PULL_UP)
BUTTON_B = Pin(22,Pin.IN,Pin.PULL_UP)
BUTTON_C = Pin(21,Pin.IN,Pin.PULL_UP)

music_index = 0
music = [E7, E7, 0, E7, 0, C7, E7, 0, G7, 0, 0, 0, G6, 0, 0, 0, C7, 0, 0, G6, 0, 0, E6, 0, 0, A6, 0, B6, 0, AS6, A6, 0, G6, E7, 0, G7, A7, 0, F7, G7, 0, E7, 0,C7, D7, B6, 0, 0, C7, 0, 0, G6, 0, 0, E6, 0, 0, A6, 0, B6, 0, AS6, A6, 0, G6, E7, 0, G7, A7, 0, F7, G7, 0, E7, 0,C7, D7, B6, 0, 0]

def notify(string):
    if DEBUG_MODE:
        print(string, gc.mem_free())
    
def blink():
    if blinker.repeat_execution():
        led.toggle()

def is_pressed(pin):
    return not pin.value()

#============================================================
# States Logic Functions
#============================================================
def idle_logic():
    if state_machine.execute_once:
        gc.collect()
        notify("Idle")
        transition_timer.start()
        led.off()
        buzzer.duty_u16(0)
    
    blink()
        
def starting_logic():
    if state_machine.execute_once:
        notify("Starting")
        transition_timer.start()
    
    if transition_timer.finished():
        state_machine.force_transition_to(execute)

def execute_logic():
    global music_index
    
    if state_machine.execute_once:
        notify("Execute")
        transition_timer.start()
        led.off()

    #--------------------------------------------------------------------------
    #  CONTINUOUS LOGIC IN EXECUTE
    #--------------------------------------------------------------------------
   
    # Use player timer to play the notes until all notes have been played
    if player.repeat_execution() and music_index < len(music):
        note = music[music_index]
        if note == 0:
            buzzer.duty_u16(0)            # 0% duty cycle
            led.off()
        else:
            buzzer.freq(note)             # set frequency (notes)
            buzzer.duty_u16(19660)        # 30% duty cycle
            led.on()
        music_index += 1

    # If all notes have been played transition to completing
    if music_index >= len(music):
        state_machine.force_transition_to(completing)

    # Suspend execution if button C is pressed during execute
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_C)):
        state_machine.force_transition_to(suspending)
        
    #--------------------------------------------------------------------------


def completing_logic():
    if state_machine.execute_once:
        notify("Completing")
        transition_timer.start()
        buzzer.duty_u16(0)
    
    if transition_timer.finished():
        state_machine.force_transition_to(completed)

def completed_logic():
    if state_machine.execute_once:
        notify("Completed")
        transition_timer.start()

    led.on()
    
def resetting_logic():
    global music_index
    
    if state_machine.execute_once:
        notify("Resetting")
        transition_timer.start()
        buzzer.duty_u16(0)
        music_index = 0
        led.off()
    
    if transition_timer.finished():
        state_machine.force_transition_to(idle)

def suspending_logic():
    if state_machine.execute_once:
        notify("Suspending")
        transition_timer.start()
        buzzer.duty_u16(0)        
    
    if transition_timer.finished():
        state_machine.force_transition_to(suspended)

def suspended_logic():
    if state_machine.execute_once:
        notify("Suspended")

    blink()
    
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_C)):
        state_machine.force_transition_to(unsuspending)

def unsuspending_logic():
    if state_machine.execute_once:
        notify("Un-suspending")
        transition_timer.start()
    
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
        buzzer.duty_u16(0)
    
    if transition_timer.finished():
        state_machine.force_transition_to(stopped)

def stopped_logic():
    if state_machine.execute_once:
        notify("Stopped")
    
    led.off()
    
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_A)):
        state_machine.force_transition_to(resetting)


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

# Main Loop: Run the state machine here
while True:

    # Run state machine state's logics
    state_machine.run()