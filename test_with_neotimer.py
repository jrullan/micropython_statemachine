from statemachine import *
from neotimer import *
from machine import Pin

led = Pin(25,Pin.OUT)
led.off()

counter = 0
myTimer = Neotimer(1000)
blinker = Neotimer(100)


myMachine = StateMachine()

#============================================================
# States Logic Functions
#============================================================
def state1_logic():
    global counter
    
    # This block of the code will execute just once
    if myMachine.execute_once:
        myTimer.start()    #<---- Start myTimer in state1
        counter += 1
        print("State 1 Logic: Blinking LED")

    # Code that executes continously during a state should go here
    # until a transition occurs    
    if blinker.repeat_execution():
        led.toggle()   

    # Define transitions to other states
    if myTimer.finished():
        myMachine.transition_to(state2)


def state2_logic():
    global counter
    if myMachine.execute_once:
        counter += 1
        print("State 2 Logic: Turn off LED")
    
    led.off()
    
def state3_logic():
    global counter
    if myMachine.execute_once:
        counter += 1
        print("State 3 Logic Executed Once")
        
    myMachine.transition_to(state4)             #<---- Force the transition to state4
        

def state4_logic():
    global counter
    if myMachine.execute_once:
        counter += 1
        print("State 4 Logic Executed Once")
    
    myMachine.transition_to(state5)             #<---- Force the transition to state5


def state5_logic():
    global counter
    if myMachine.execute_once:
        counter += 1
        print("State 5 Logic Executed Once")
    
    myMachine.current_state_index = -1          #<---- Exit machine execution


#============================================================
# State Transitions Functions
#
# These are predefined transition functions that must evaluate
# to True or False.
#
# Alternatively, you can force transitions during the state logic
# (See state3_logic and state4_logic)
#============================================================
# def state1_transition_to_2():
#     return True                                     #<---- Transition from state1 to state2 immediately

# def state2_transition_to_3():
#     return (True if myTimer.finished() else False)  #<---- Transition from state2 to state3 when myTimer finishes


#============================================================
# Add states to machine
#============================================================
state1 = myMachine.add_state(state1_logic)

state2 = myMachine.add_state(state2_logic)

state3 = myMachine.add_state(state3_logic)

state4 = myMachine.add_state(state4_logic)

state5 = myMachine.add_state(state5_logic)


#============================================================
# Add transitions to states
#============================================================
# state1.add_transition(state1_transition_to_2, state2)

# state2.add_transition(state2_transition_to_3, state3) # lambda : True
state2.add_transition(lambda: True, state3)

while True:
    if myMachine.run() == -1:
        break
    
# while counter < len(myMachine.state_list):
#     myMachine.run()