from statemachine import *

counter = 0
myMachine = StateMachine()

#============================================================
# States Logic Functions
#============================================================

def state1_logic():
    global counter
    
    if myMachine.execute_once:
        counter += 1
        print("State 1 Execution")
   
   
def state2_logic():
    global counter
    
    if myMachine.execute_once:
        counter += 1
        print("State 2 Execution")
    
    
def state3_logic():
    global counter
    
    if myMachine.execute_once:
        counter += 1
        print("State 3 Execution")

#============================================================
# State Transitions Functions
#============================================================

def transition_1_to_2():
    return True


def transition_2_to_3():
    return True

#============================================================
# Add states to machine
#============================================================

state1 = myMachine.add_state(state1_logic)
state2 = myMachine.add_state(state2_logic)
state3 = myMachine.add_state(state3_logic)


#============================================================
# Add transitions to states
#============================================================

state1.add_transition(transition_1_to_2, state2)
state2.add_transition(transition_2_to_3, state3)


while counter < len(myMachine.state_list):
    myMachine.run()
    print("counter",counter)