class StateMachine:
    def __init__(self,start_state,transitions):
        self.next_state = None
        self.cur_state = start_state
        self.transitions = transitions
        self.cur_state.enter(None)

    def update(self):
        self.cur_state.do()

    def draw(self):
        self.cur_state.draw()

    def handle_state_event(self, state_event):
        if state_event[0] in self.transitions[self.cur_state]:
            next_state_func = self.transitions[self.cur_state][state_event[0]]
            next_state = next_state_func(state_event)
            self.cur_state.exit(state_event)
            self.cur_state = next_state
            self.cur_state.enter(state_event)
            return True
        return False
