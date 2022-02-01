from statemachine import *
from neotimer import *

counter = 0
myTimer = Neotimer(1000)
myMachine = StateMachine()

#============================================================
# States Logic Functions
#============================================================
def state1_logic():
    global counter
    if myMachine.execute_once:
        
        myTimer.start()    #<---- Start myTimer in state1
        counter += 1
        print("State 1 Logic Executed Once")
   
   
def state2_logic():
    global counter
    if myMachine.execute_once:
        
        counter += 1
        print("State 2 Logic Executed Once")
    
    
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
        
        
#============================================================
# State Transitions Functions
#
# These are predefined transition functions that must evaluate
# to True or False.
#
# Alternatively, you can force transitions during the state logic
# (See state3_logic)
#============================================================
def state1_transition_to_2():
    return True                                     #<---- Transition from state1 to state2 immediately

def state2_transition_to_3():
    return (True if myTimer.finished() else False)  #<---- Transition from state2 to state3 when myTimer finishes


#============================================================
# Add states to machine
#============================================================
state1 = myMachine.add_state(state1_logic)

state2 = myMachine.add_state(state2_logic)

state3 = myMachine.add_state(state3_logic)

state4 = myMachine.add_state(state4_logic)


#============================================================
# Add transitions to states
#============================================================
state1.add_transition(state1_transition_to_2, state2)

state2.add_transition(state2_transition_to_3, state3) # lambda : True


while counter < len(myMachine.state_list):
    myMachine.run()
