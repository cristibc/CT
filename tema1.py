def shunting_yard(expression):
    output = []
    operator_stack = []
    precedence = {'*': 4, '.':3, '|': 2, '(': 1}

    for token in expression:
        if token.isalnum():
            output.append(token)
        elif token == '(':
            operator_stack.append(token)
        elif token == ')':
            while operator_stack and operator_stack[-1] != '(':
                output.append(operator_stack.pop())
            operator_stack.pop()
        else:
            while operator_stack and precedence.get(operator_stack[-1], 0) >= precedence.get(token, 0):
                output.append(operator_stack.pop())
            operator_stack.append(token)

    while operator_stack:
        output.append(operator_stack.pop())

    return output

def infix_to_postfix(regex):
    modified_regex = ''
    for i in range(len(regex)):
        modified_regex += regex[i]
        if i < len(regex) - 1 and regex[i].isalnum() and regex[i + 1].isalnum():
            modified_regex += '.'

    return shunting_yard(modified_regex)

class State:
    def __init__(self, is_final=False):
        self.is_final = is_final
        self.transitions = {}
        self.lambda_transitions = set()
        self.label = None

    def add_transition(self, symbol, target):
        self.transitions[symbol] = target

    def add_lambda_transition(self, target):
        self.lambda_transitions.add(target)

    def __str__(self):
        return f"State({self.label})"

    __repr__ = __str__

def thompson(postfix):
    stack = []
    state_counter = 0

    for token in postfix:
        if token.isalnum():
            start = State()
            end = State(True)
            start.add_transition(token, end)
            stack.append((start, end))
        elif token == '|':
            start, end = State(), State()
            sub_start_1, sub_end_1 = stack.pop()
            sub_start_2, sub_end_2 = stack.pop()
            start.add_lambda_transition(sub_start_1)
            start.add_lambda_transition(sub_start_2)
            sub_end_1.add_lambda_transition(end)
            sub_end_2.add_lambda_transition(end)
            sub_end_1.is_final = False
            sub_end_2.is_final = False
            end.is_final = True
            stack.append((start, end))
        elif token == '.':
            sub_start_2, sub_end_2 = stack.pop()
            sub_start_1, sub_end_1 = stack.pop()
            sub_end_1.is_final = False
            sub_end_1.add_lambda_transition(sub_start_2)
            stack.append((sub_start_1, sub_end_2))
        elif token == '*':
            start, end = State(), State()
            sub_start, sub_end = stack.pop()
            start.add_lambda_transition(sub_start)
            start.add_lambda_transition(end)
            sub_end.add_lambda_transition(sub_start)
            sub_end.add_lambda_transition(end)
            sub_end.is_final = False
            end.is_final = True
            stack.append((start, end))

    start_state, end_state = stack.pop()
    states = set()
    transitions = {}
    visited = set()

    def dfs(state):
        nonlocal state_counter
        if state in visited:
            return
        visited.add(state)
        state.label = state_counter
        state_counter += 1
        states.add(state)
        for symbol, target in state.transitions.items():
            transitions.setdefault(state, []).append((symbol, target))
            dfs(target)
        for target in state.lambda_transitions:
            dfs(target)

    dfs(start_state)

    return start_state, states

def display_graph(start_state, states):
    import graphviz

    dot = graphviz.Digraph()
    dot.attr(rankdir='LR')

    for state in states:
        if state.is_final:
            dot.node(str(state.label), str(state.label), root='true', shape='doublecircle')
        else:
            dot.node(str(state.label), str(state.label))

    for state in states:
        for symbol, target in state.transitions.items():
            dot.edge(str(state.label), str(target.label), label=symbol)
        for target in state.lambda_transitions:
            dot.edge(str(state.label), str(target.label), label="λ")

    dot.render('automaton', view=True)

if __name__ == "__main__":
    regex_input = input("Introduceti o expresie regulata: ")
    postfix_output = infix_to_postfix(regex_input)
    print("Expresia in postfix:", ''.join(postfix_output))

    start_state, states = thompson(postfix_output)
    display_graph(start_state, states)

