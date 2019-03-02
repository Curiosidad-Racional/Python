from inspect import isclass
from traceback import format_exception
from collections.abc import Iterable

def node_format(item):
    if hasattr(item, "__name__"):
        return item.__name__
    else:
        return type(item).__name__

def graph_format(item):
    if isinstance(item, dict):
        if not item:
            return "{}"
        string = "{"
        for key, value in item.items():
            string += key.__name__ + ": "
            if isinstance(value, dict):
                if not value:
                    string += "{}"
                else:
                    string += "{"
                    for k, v in value:
                        string += k.__name__ + ": " + node_format(v) + ", "
                    string = string[:-2] + "}, "
            else:
                string += node_format(value) + ", "
        string = string[:-2] + "}"
    elif isinstance(item, Iterable):
        if not item:
            return "[]"
        string = "["
        for i in item:
            string += node_format(i) + ", "
        string = string[:-2] + "]"
    else:
        string = node_format(item)
    return string


class Event:
    pass


class Exit(Event):
    def __init__(self, event):
        self.event = event


class Start(Event):
    def __init__(self, event):
        self.event = event


class Subject:
    def __init__(self):
        self._observers = []

    def register(self, observer):
        self._observers.append(observer)

    def notify_all(self, event):
        for observer in self._observers:
            observer.notify(event)


class Observer:
    def notify(self, event):
        raise NotImplementedError()

    def fetch(self):
        raise NotImplementedError()


class State(Subject):
    def _enter_(self, event, from_state):
        raise NotImplementedError()

    def _exit_(self, event, to_state, exc):
        pass


class StopMachine(Exception):
    def __init__(self, event):
        self.event = event


class Machine(State, Observer):  # Prepared to be State
    def __init__(self, states=None, transitions=None, notifiers=None):
        super().__init__()
        self._state = None
        self._states = {}
        for state in states or self.states:
            self._states[type(state)] = state
            state.register(self)
        if transitions:
            self.transitions = transitions
            for state, transitions in transitions.items():
                self._states[state].transitions = transitions
        elif not hasattr(self, "transitions"):
            self.transitions = {}
        if notifiers:
            self.notifiers = notifiers
        self._type = type(self)

    def _enter_(self, event, from_state):
        # [ <first>
        # Simulates Start event. Enter into first machine state.
        # Machines cannot handle their own state, then have to
        # enter immediately in their first state.
        try:
            # Machines' transitions have to have Start event
            try:
                function_or_type = self.transitions[Start]
            except KeyError as e:
                e.args = (str(e.args[0]) + "   Missing: Start"
                          + " in: " + type(self._state).__name__
                          + " transitions: " + graph_format(self._state.transitions),)
                raise
            if function_or_type is self._type:
                # Machines cannot point to themselves
                raise ValueError("Machine Start: Machine. Infinite loop")
            elif isclass(function_or_type):
                state_type = function_or_type
            else:
                raise TypeError("Not state: " + str(function_or_type))
            # Obtain fisrt state instance
            try:
                state = self._states[state_type]
            except KeyError as e:
                e.args = (str(e.args[0]) + "   Missing: " + state_type.__name__
                          + " in: " + type(self).__name__
                          + " states: " + graph_format(self._states.keys()),)
                raise
            # Enter into first state instance
            self._state = state
            # <PRINT enter start self>
            self._state._enter_(Start(event), self)
        except StopMachine as e:
            if self._observers:
                # Machines' transitions then has to contain Exit transition
                self.notify_all(Exit(e.event))
            else:
                # <PRINT exit start stop self>
                self._exit_(e.event, None, None)
            return
        except BaseException as e:
            if self._observers:
                raise
            else:
                # <PRINT exit start exception self>
                if self._exit_(None, None, e) is None:
                    raise
        # ] <first>
        # [ <loop>
        # Machines' main event loop. Fetch and process events.
        # Contains machines' logic.
        while True:
            try:
                try:
                    # Get next event
                    event = self.fetch()
                    event_type = type(event)
                    # If event in Machine's transitions cannot handle it.
                    # Exit controlled calling to current state function
                    # if exists
                    if event_type in self.transitions:
                        # If upper event in state transitions then call
                        # its function value
                        if event_type in self._state.transitions:
                            function = self._state.transitions[event_type]
                            # This value cannot be a state because the event
                            # has to be hancdled by upper machine.
                            # Then state value has to be in current machine
                            # transitions and not in current state transitions
                            if isclass(function):
                                raise ValueError("Upper event: " + event_type.__name__
                                                 + " value: " + function.__name__
                                                 + " in:" + graph_format(self._state.transitions)
                                                 + " hasn't to be class")
                            function(event)
                        # Exit controlled
                        raise StopMachine(event)
                    try:
                        function_or_type = self._state.transitions[event_type]
                    except KeyError as e:
                        e.args = (str(e.args[0]) + "   Missing: " + event_type.__name__
                                  + " in: " + type(self._state).__name__
                                  + " transitions: " + graph_format(self._state.transitions),)
                        raise
                    # Transitions values states and callable objects allowed
                    if function_or_type is self._type:
                        # Transition to itself involve Exit
                        raise StopMachine(event)
                    elif isclass(function_or_type):
                        # Next state type
                        state_type = function_or_type
                    elif callable(function_or_type):
                        # We still don't leave current state
                        function_or_type(event)
                        continue
                    else:
                        raise TypeError("Neither function nor state: " + str(function_or_type))
                    # Next state
                    try:
                        state = self._states[state_type]
                    except KeyError as e:
                        e.args = (str(e.args[0]) + "   Missing: " + state_type.__name__
                                  + " in: " + type(self).__name__
                                  + " states: " + graph_format(self._states.keys()),)
                        raise
                except StopMachine as e:
                    # Controlled state exit then machine stop
                    # <PRINT exit stop state>
                    self._state._exit_(e.event, self, None)
                    raise
                except BaseException as e:
                    # Controlled state exit
                    # <PRINT exit exception state>
                    if self._state._exit_(None, self, e) is None:
                        raise
                else:
                    # Next state then exit current state
                    # <PRINT exit state>
                    self._state._exit_(event, state, None)
                # Begin transition
                from_state = self._state
                self._state = None
                transition = (type(from_state), state_type)
                if transition in from_state.transitions:
                    from_state.transitions[transition](event, from_state, state)
                # End transition entering in next state
                self._state = state
                # <PRINT enter state>
                self._state._enter_(event, from_state)
            except StopMachine as e:
                # Whether upper machine then upper machine handle exit
                # else current machine exits by itself
                if self._observers:
                    # Machines' transitions then has to contain Exit transition
                    self.notify_all(Exit(e.event))
                else:
                    # <PRINT exit stop self>
                    self._exit_(e.event, self, None)
                return
            except BaseException as e:
                # Whether upper machine then upper machine handle exit
                # else current machine exits by itself
                if self._observers:
                    raise
                else:
                    # <PRINT exit exception self>
                    if self._exit_(None, None, e) is None:
                        raise
        # ] <loop>

    def start(self, event=None, from_state=None):
        # <PRINT machine start>
        self._enter_(event, from_state)

    def notify(self, event):
        try:
            notifier = self.notifiers[type(event)]
        except KeyError as e:
            e.args = (str(e.args[0]) + "   Missing: " + type(event).__name__
                      + " in: " + type(self).__name__
                      + " notifiers: " + graph_format(self.notifiers))
            raise
        if isinstance(notifier, tuple):
            self.__dict__[notifier[0]] = event.__dict__[notifier[1]]
        else:
            return notifier(event)


if __name__ == "__main__":
    from queue import Queue


    class Next(Event):
        pass


    class Yes(Event):
        pass


    class No(Event):
        pass

    queue = Queue()


    class QueueObserver(Observer):
        def notify(self, event):
            queue.put(event)

        def fetch(self):
            return queue.get()


    class Startup(State):
        def __init__(self):
            super().__init__()
            self.transitions = {Next: AbortCondition}

        def _enter_(self, event, state):
            self.notify_all(Next())


    class AbortCondition(State):
        def __init__(self):
            super().__init__()
            self.transitions = {No: Mutex, Yes: Starter}
            self.first = True

        def _enter_(self, event, state):
            if self.first:
                self.first = False
                self.notify_all(No())
            else:
                self.notify_all(Yes())


    class Mutex(QueueObserver, Machine):
        def __init__(self, states):
            super().__init__(states)
            self.transitions = {Start: LaunchCondition, Exit: AbortCondition}


    class LaunchCondition(State):
        def __init__(self):
            super().__init__()
            self.transitions = {Next: Launch}

        def _enter_(self, event, state):
            self.notify_all(Next())


    class Launch(State):
        def __init__(self):
            super().__init__()
            self.transitions = {Next: Mutex}

        def _enter_(self, event, state):
            self.notify_all(Next())


    class Starter(QueueObserver, Machine):
        def __init__(self, states):
            super().__init__(states)
            self.transitions = {Start: Startup}


    Starter([Startup(), AbortCondition(), Mutex([LaunchCondition(), Launch()])]).start()