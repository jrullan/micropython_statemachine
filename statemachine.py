class Transition:
    def __init__(self, function, state):
        self.function = function
        self.to_state_number = state.index



class StateMachine:
    def __init__(self):
        self.state_list = []
        self.current_state = -1     #Indicates the current state number
        self.execute_once = True    #Indicates that a transition to a different state has occurred

    # Creates a new state and adds it to the list
    # using the state_logic_function passed as parameter
    def add_state(self, state_logic_function):
        state = State(state_logic_function)
        state.index = len(self.state_list)
        self.state_list.append(state)
        return state

    # Runs the state machine
    def run(self):
        if len(self.state_list) == 0:
            return
        
        if self.current_state == -1:
            self.current_state = 0
        
        # Store current state to check if it changed during execution
        initial_state = self.current_state
        
        # Execute the state's logic and get the next_state number
        # If no transition ocurred returns it's own index as the next state index.
        next_state = self.state_list[self.current_state].execute()
        
        # If current_state remains the same then 
        if initial_state == self.current_state:
            # If a different state number was returned, execute_once is True
            if self.current_state != next_state:
                self.execute_once = True
            else:
                self.execute_once = False
            self.current_state = next_state



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



    