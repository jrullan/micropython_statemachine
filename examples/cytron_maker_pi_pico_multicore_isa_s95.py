DEBUG_MODE = True

import _thread,gc
from neotimer import *                    #<---- 3,088 bytes
from statemachine import *                #<---- 3,616 bytes
from pitches import *
from machine import Pin, PWM
import time

state_machine = StateMachine()           #<--- 96 bytes
debouncing_timer = Neotimer(200)         #<--- 64 bytes

one_second_hold = Neotimer(1000)
transition_timer = Neotimer(300)
player_tempo = 150
player = Neotimer(player_tempo)
blinker = Neotimer(player_tempo/2)

led = Pin(25,Pin.OUT)
led.off()

buzzer = machine.PWM(machine.Pin(18))  # set pin 18 as PWM OUTPUT

# Cytron onboard buttons
BUTTON_1 = Pin(20,Pin.IN,Pin.PULL_UP)
BUTTON_2 = Pin(21,Pin.IN,Pin.PULL_UP)
BUTTON_3 = Pin(22,Pin.IN,Pin.PULL_UP)

music_index = 0
music = [E7, E7, 0, E7, 0, C7, E7, 0, G7, 0, 0, 0, G6, 0, 0, 0, C7, 0, 0, G6, 0, 0, E6, 0, 0, A6, 0, B6, 0, AS6, A6, 0, G6, E7, 0, G7, A7, 0, F7, G7, 0, E7, 0,C7, D7, B6, 0, 0, C7, 0, 0, G6, 0, 0, E6, 0, 0, A6, 0, B6, 0, AS6, A6, 0, G6, E7, 0, G7, A7, 0, F7, G7, 0, E7, 0,C7, D7, B6, 0, 0]

free_memory_threshold = 0
lock = _thread.allocate_lock()

# Setup pins from 0 to 15 
for i in range(16):                      
    machine.Pin(i,machine.Pin.OUT)

leds_value = False
    

def notify(string):
    if DEBUG_MODE:
        print(string)
    
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
        notify("Idle")
        notify("Adjust tempo by pressing button 2 (+) or button 3 (-)")
        transition_timer.start()
        led.off()
        buzzer.duty_u16(0)
    
    blink()
    
    # Suspend execution if button C is pressed during execute
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_2)):
        player.duration += 5
        blinker.duration = player.duration
        print("Tempo: ", player.duration)

    # Suspend execution if button C is pressed during execute
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_3)):
        player.duration -= 5
        blinker.duration = player.duration
        print("Tempo: ", player.duration)
        
        
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
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_2)):
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

    if transition_timer.finished():
        state_machine.force_transition_to(resetting)
    
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
        print()

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
    
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_2)):
        state_machine.force_transition_to(unsuspending)

def unsuspending_logic():
    if state_machine.execute_once:
        notify("Un-suspending")
        transition_timer.start()
    
    if transition_timer.finished():
        state_machine.force_transition_to(execute)

def stopping_logic():
    if state_machine.execute_once:
        notify("Stopping")
        transition_timer.start()
        buzzer.duty_u16(0)
    
    if transition_timer.finished() and not is_pressed(BUTTON_3):
        state_machine.force_transition_to(stopped)

def stopped_logic():
    if state_machine.execute_once:
        notify("Stopped")
        led.off()
   
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_1)):
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
stopping = state_machine.add_state(stopping_logic)
stopped = state_machine.add_state(stopped_logic)


#============================================================
# State Transitions Functions (optional)
#============================================================
def next_transition():
    if debouncing_timer.debounce_signal(is_pressed(BUTTON_1)) and transition_timer.finished():  #<---- Advance condition
        return True
    else:
        return False

def stop_transition():
    if one_second_hold.hold_signal(is_pressed(BUTTON_3)):
        return True
    else:
        return False
    
#============================================================
# Attach transitions to states (optional)
#============================================================
# Attach transitions to all states
for state in state_machine.state_list:
    if state.index != 0:  #<---- All states except IDLE
        state.attach_transition(stop_transition, stopping)

idle.attach_transition(next_transition,starting)
execute.attach_transition(next_transition,completing)
completed.attach_transition(next_transition,resetting)



##########################################################################
# Main loops for Core 0 and Core 1
##########################################################################

# This will be running on Core 0
def running_lights():   
    global free_memory_threshold
    global leds_value
    
    # Manually invoke garbage collection
    if gc.mem_free() < free_memory_threshold:
        #lock.acquire()
        gc.collect()
        #lock.release()

    leds_value = not leds_value

    # turn on or off all leds sequentially
    for i in range(16):
        machine.Pin(i).value(leds_value)
        time.sleep(0.1)
    
            
# This will be running on Core 1
def state_machine_logic():  

    while True:
        
        state_machine.run()

#======> MULTICORE EXECUTION OF state_machine_logic() <=======
# Start state_machine_logic() on Core 1
_thread.start_new_thread(state_machine_logic, ())

# Determine how much memory is free before starting
# main loop in Core 0. This will be used as threshold
# to determine if we should invoke gc.collect()
gc.collect()
free_memory_threshold = gc.mem_free()
print("Free memory",free_memory_threshold)
#=============================================================

# Main Loop - Asynchronous or Continuous Logic Here
while True:
    running_lights()