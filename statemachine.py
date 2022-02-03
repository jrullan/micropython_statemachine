#============================================================================
# The state machine is composed of three different classes.
#
#  1. StateMachine - This is the class that executes and configures
#     the states and transitions. A state machine contains a list of states.
#
#  2. State - This class implements a state consisting of it's execution
#     logic and it's list of transitions. When the machine executes a state,
#     it's logic is executed and all of its transitions are evaluated.
#     The first transition to evaluate to True is used by the machine
#     to determine its next state. A state contains a list of transitions.
#     During execution of a state logic, a flag called execute_once is True
#     during the first execution of a state logic. This is very useful to
#     run a logic only once when the state is first active. The remaining
#     logic other than the one in the execute_once block is executed continously
#     until a transition returns True.
#
#         def state1_logic():
#             global counter
#             
#             if myMachine.execute_once:
#                 myTimer.start()                       }   
#                 counter += 1                          }   Code that executes only the first time the state is active. 
#                 print("State 1 Logic: Blinking LED")  }
#
#             do_something()                            }   Call do_something() while waiting for a transition to be active
#         ...
#         state1 = myMachine.add_state(state1_logic)
#         ...
#
#  3. Transition - This class is used to store a function that will
#     execute and return a boolean value of True or False. If it evaluates
#     to True, the state will use the transition's to_state_number to
#     tell the machine what the next state should be.
#
#
#         def state1_transition_to_2():
#             if some_condition == True:
#                 return True             #<---- Transition when some_condition is True
#             else:
#                 return False
#
# 
#         state1.add_transition(state1_transition_to_2, state2)   #<---- Attach state1 transition to state2, when some_condition == True
#
#
#  4. Forced transitions
#     An alternative way to specify the transitions without creating
#     transition objects is to use the state machine's transition_to()
#     method. This method will force the transition to another state,
#     bypassing any transitions attached to a particular state. This
#     approach also has the benefit of not requiring the creation of
#     transition objects, and the code could be leaner. One way of
#     using this feature is to use it inside the state logic as
#     in the example below:
# 
#         def state1_logic():
#             global counter
#             
#             if myMachine.execute_once:
#                 myTimer.start()
#                 counter += 1
#                 print("State 1 Logic: Blinking LED")
# 
#             if myTimer.finished():
#                 myMachine.transition_to(state2)   #<---- If timer has finished force transition to state2
# 
#
# Author: José Rullán
# Date: February 1, 2022
#============================================================================


class Transition:
    def __init__(self, function, state):
        self.function = function
        self.to_state_number = state.index



class StateMachine:
    def __init__(self):
        self.state_list = []
        self.active_state_index = -1     #Indicates the current state number
        self.execute_once = True    #Indicates that a transition to a different state has occurred
        
        # Jog mode is used to prevent transitions including using transition_to
        # The jog() method will execute each state sequentially preventing transitions.
        self.jog_mode = False

    # Creates a new state and adds it to the list
    # using the state_logic_function passed as parameter
    def add_state(self, state_logic_function):
        state = State(state_logic_function)
        state.index = len(self.state_list)
        self.state_list.append(state)
        if self.active_state_index == -1:    #<---- Initially set active_state_index to 0
            self.active_state_index = 0
        return state

    # Forces a transition to a particular state
    def transition_to(self, state):
        if self.jog_mode:
            return -1
        self.active_state_index = state.index
        self.execute_once = True
        return state.index

    # If jog_mode is True, each time jog() is called it will
    # execute the next state in state_list, wrapping around
    # to the first state when all have been called
    def jog(self):
        if not self.jog_mode:
            return  
        self.active_state_index += 1
        if self.active_state_index >= len(self.state_list):
            self.active_state_index = 0
        self.execute_once = True

    # Runs the state machine
    def run(self):
        if len(self.state_list) == 0:
            return -1
        
        # Store current state to check if it changed during execution
        current_state_index = self.active_state_index
        
        # Execute the state's logic and get the next_state_index number
        # If no transition ocurred returns it's own index as the next state index.
        next_state_index = self.state_list[self.active_state_index].execute()
        
        # Process the transition if current_state remains the same after the state logic
        # (This check is to ignore the transitions if the current_state has been modified
        # by the state logic, or externally by the machine)
        if current_state_index == self.active_state_index:
            # If a different state number was returned, execute_once is True
            if self.active_state_index != next_state_index:
                self.execute_once = True
            else:
                self.execute_once = False                            
            # Finally make the next state the current state, unless
            # jog_mode is True, in which case the next state index
            # would be the next sequential index when jog() is called.
            if not self.jog_mode:
                self.active_state_index = next_state_index
        
        return self.active_state_index



class State:
    def __init__(self, logic_function):
        self.transitions = []
        self.logic = logic_function
        self.index = -1
    
    def add_transition(self, transition_function, state):
        transition = Transition(transition_function, state)
        self.transitions.append(transition) 
    
    def eval_transitions(self):
        if len(self.transitions) == 0:
            return self.index
        
        result = False
        for transition in self.transitions:
            result = transition.function()
            if result:
                return transition.to_state_number
            
        return self.index
    
    def execute(self):
        self.logic()
        return self.eval_transitions()