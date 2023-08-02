
#from micropython import const
from machine import Pin
import sys
from collections import OrderedDict
import uasyncio as asyncio
import ntptime

from delay_ms import Delay_ms

from config import PINS
from scenarios import STATES, TRANSITIONS
from motor import Motor


class Condition:
    """ A helper class to call condition checks in the intended way.
    Attributes:
        func (str or callable): The function to call for the condition check
        target (bool): Indicates the target state--i.e., when True,
                the condition-checking callback should return True to pass,
                and when False, the callback should return False to pass.
    """

    def __init__(self, func, target=True):
        """
        Args:
            func (str or callable): Name of the condition-checking callable
            target (bool): Indicates the target state--i.e., when True,
                the condition-checking callback should return True to pass,
                and when False, the callback should return False to pass.
        Notes:
            This class should not be initialized or called from outside a
            Transition instance, and exists at module level (rather than
            nesting under the transition class) only because of a bug in
            dill that prevents serialization under Python 2.7.
        """
        self.func = func
        self.target = target

    def check(self, machine):
        """ Check whether the condition passes.
        """
        predicate = machine.resolve_callable(self.func)

        return predicate() == self.target

    def __repr__(self):
        return "<%s(%s)@%s>" % (type(self).__name__, self.func, id(self))



class Transition:
    """ Representation of a transition managed by a ``Machine`` instance.
    Attributes:
        source (str): Source state of the transition.
        dest (str): Destination state of the transition.
        prepare (list): Callbacks executed before conditions checks.
        conditions (list): Callbacks evaluated to determine if
            the transition should be executed.
        before (list): Callbacks executed before the transition is executed
            but only if condition checks have been successful.
        after (list): Callbacks executed after the transition is executed
            but only if condition checks have been successful.
    """

    condition_cls = Condition
    """ The class used to wrap condition checks. Can be replaced to alter condition resolution behaviour
        (e.g. OR instead of AND for 'conditions' or AND instead of OR for 'unless') """

    def __init__(self, source=None, dest=None, conditions=None, unless=None, before=None,
                 after=None, prepare=None, on_enter_state=None, on_exit_state=None):
        """
        Args:
            source (str): The name of the source State.
            dest (str): The name of the destination State.
            conditions (optional[str, callable or list]): Condition(s) that must pass in order for
                the transition to take place. Either a string providing the
                name of a callable, or a list of callables. For the transition
                to occur, ALL callables must return True.
            unless (optional[str, callable or list]): Condition(s) that must return False in order
                for the transition to occur. Behaves just like conditions arg
                otherwise.
            before (optional[str, callable or list]): callbacks to trigger before the
                transition.
            after (optional[str, callable or list]): callbacks to trigger after the transition.
            prepare (optional[str, callable or list]): callbacks to trigger before conditions are checked
        """
        self.source = source

        self.dest = dest

        self.prepare = [self._check_source_dest] # Check - what for? is it necessary
        self.before = [self._check_allowed_states]
        self.after = []

        self.on_enter_state = on_enter_state
        self.on_exit_state= on_exit_state

        self.conditions = []
        if conditions is not None:
            for cond in conditions:
                self.conditions.append(self.condition_cls(cond))
        if unless is not None:
            for cond in unless:
                self.conditions.append(self.condition_cls(cond, target=False))

        self.add_callback('prepare', prepare)
        self.add_callback('before', before)
        self.add_callback('after', after)

    def _eval_conditions(self, machine):
        for cond in self.conditions:
            if not cond.check(machine):
                return False
        return True

    def execute(self, machine):
        """ Execute the transition.
        Args:
            machine: An instance of class StateMachine.
        Returns: boolean indicating whether the transition was
            successfully executed (True if successful, False if not).
        """
        #self.source = self.model.state.name if self.model.state else None

        machine.callbacks(self.prepare)

        if not self._eval_conditions(machine):
            return False

        machine.callbacks(self.before)

        if self.dest:  # if self.dest is None this is an internal transition with no actual state change
            self._change_state(machine)

        machine.callbacks(self.after)

        machine.model.rotate()

        self.add_state_callback(machine, 'on_enter', self.on_enter_state)

        self.add_state_callback(machine, 'on_exit', self.on_exit_state)

        return True

    def _change_state(self, machine):
        machine.go_to_state(self.dest)

    def _check_source_dest(self):
        if self.source == self.dest:
            self.dest = None

    def _check_allowed_states(self):
        if not self.dest in STATES.keys():
            self.dest = None

    def add_callback(self, trigger, func): # PASS
        """ Add a new before, after, or prepare callback.
        Args:
            trigger (str): The type of triggering event. Must be one of
                'before', 'after' or 'prepare'.
            func (str or callable or list): The name of the callback function or a callable.
        """
        callback_list = getattr(self, trigger)
        if isinstance(func, list):
            callback_list.extend(func)
        elif isinstance(func, dict):
            pass#turn a dictionary key to a callable with the value(s) as the argument
        else:
            callback_list.append(func)


    #  Check Not using thi either - confirm
    def add_state_callback(self, machine, trigger, func): # Check I don't think this is needed
        pass
        """ Add a new on_enter and on_exit callback.
        Args:
            trigger (str): The type of triggering event. Must be one of
                'on_exit', 'on_before'.
            func (str or callable or list): The name of the callback function or a callable.
        """
        callback_list = getattr(machine.model.current_state, trigger)

        if isinstance(func, list):
            callback_list.extend(func)
        elif isinstance(func, dict):
            pass#turn a dictionary key to a callable with the value(s) as the argument
        else:
            callback_list.append(func)


    def __repr__(self):
        return "<%s('%s', '%s')@%s>" % (type(self).__name__,
                                        self.source, self.dest, id(self))



#state machine class
class StateMachine:
    name = 'Platform Rotation System'

    transition_cls = Transition

    divisions = len(STATES)

    def __init__(self, plat_div):

        self.model = Platform(plat_div)

        self.delay = Delay_ms(self._run_transitions, ())

        self.transition_generator = self.create_transition()

        self.transition_time, self.transition = next(self.transition_generator)

        print(self.transition_time)
        print(self.transition)

        self.delay.trigger(self.transition_time)

    def create_transition(self):
        for key in range(len(TRANSITIONS)):
            name, trans = TRANSITIONS[key]

            state_name = name

            transition_time = trans['transition_time']

            #for conditions and unless to work, we might need to consider the use of an asyn queue instead of generator.
            conditions = trans['conditions']
            unless = trans['unless']

            before = trans['before']
            after = trans['after']
            prepare = trans['prepare']

            on_enter = trans['on_enter']
            on_exit = trans['on_exit']

            print(self.model.current_state)
            yield transition_time, self.transition_cls(self.model.current_state.name, state_name, conditions, unless, before, after, prepare, on_enter, on_exit) # how to put an obj back into the generator in the case a condition fails?  Use the queue instead

    # // Check it's usage
    def _run_transitions(self): # PASS
        # self.transition is the next transition we want to perform
        condition = self.transition.execute(self)

        if condition:
            try:
                self.transition_time, self.transition = next(self.transition_generator)

                print(self.transition_time)
                print(self.transition)

                self.delay.trigger(self.transition_time)
            except RuntimeError:
                self.delay = None  # kill the machine or something
        else:
            self.trigger(5000) # in case the condition fails, try it again every 5 mins until it passes.

    def go_to_state(self, state_name):
        if self.model.current_state:
            self.model.old_state = self.model.current_state
            self.model.current_state.exit(self)

        self.model.current_state = self.model.states[state_name]
        self.model.current_state.enter(self)# the machine instance has been passed in

    def callbacks(self, funcs):
        """ Triggers a list of callbacks """
        for func in funcs:
            self.callback(func)

    # I changed somehting here
    def callback(self, func):
        """ Trigger a callback function with passed event_data parameters. In case func is a string,
            the callable will be resolved from the passed model in event_data. This function is not intended to
            be called directly but through state and transition callback definitions.
        Args:
            func (str): we try to import string assuming it is a path to a func
        """

        func = self.resolve_callable(func)
        func()

    @staticmethod
    def resolve_callable(func): # PASS
        """ Converts a model's property name, method name or a path to a callable into a callable.
            If func is not a string it will be returned unaltered.
        Args:
            func (str or callable): Property name, method name or a path to a callable
        Returns:
            callable function resolved from string or func
        """
        if isinstance(func, str):
            try:
                module_name, func_name = func.rsplit('.', 1)
                module = __import__(module_name.split('.')[0])
                for submodule_name in module_name.split('.')[1:]:
                    module = getattr(module, submodule_name)
                func = getattr(module, func_name)
            except (ImportError, AttributeError, ValueError):
                raise AttributeError("Callable with name '%s' could neither be retrieved from the passed "
                                        "model nor imported from a module." % func)
        return func

    async def update(self):
        await asyncio.sleep_ms(1)
        self.model.current_state.update(self)


#abstract state base class
class State:
    def __init__(self, name):
        self.name = name
        self.on_enter = STATES[self.name]['on_enter'] # Check storing in multiple places - not needed
        self.on_exit = STATES[self.name]['on_exit']

    def enter(self, machine):
        #read actions to be taken from STATE
        for fn in self.on_enter:
            if isinstance(fn, dict): # it contains the fn name as key and args as values
                fn_name, fn_args = fn.items()
                func = machine.resolve_callable(fn_name)
                func(fn_args)
            elif isinstance(fn, str):
                func = machine.resolve_callable(fn)
                func()



    def exit(self, machine):
        #read actions to be taken from STATE
        for fn in self.on_exit:
            if isinstance(fn, dict): # it contains the fn name as key and args as values
                fn_name, fn_args = fn.items()
                func = machine.resolve_callable(fn_name)
                func(fn_args)
                # cls_name, met_name = fn_name.split('_', 1)
                # getattr(cls_name, met_name)(fn_args) # make sure the fn takes *args and **kwargs
            elif isinstance(fn, str):
                func = machine.resolve_callable(fn)
                func()


    def update(self, machine): #runs updates globally for all states entered
        pass


AUTOMATION = False
class Platform(): # PASS

    def __init__(self, divisions):
        self.divisions = divisions
        self.motor = Motor(PINS)
        self.current_state = State(name='Scene_0')
        self.old_state = None
        self.states = {}
        self.locations = [(360//int(self.divisions))*i for i in range(1,int(self.divisions)+1)]

        self.locations.insert(0, 0)

        for i in range(0, self.divisions+1):
            self.states[f'Scene_{i}'] = State(name=f'Scene_{i}')

        if AUTOMATION:
            import serial
            self.platform = serial.Serial('/dev/pts/2',115200) #remember to change the port number

    def calibrate(self, reverse=False): # Just to set our motor to first division(state 1) facing us
        self.motor.move_one_step(reverse)

    def get_rotate_direction(self):
        print("reached")
        old_div_pos = int(self.old_state.name[-1])
        next_div_pos = int(self.current_state.name[-1])

        anti_clockwise_distance = (next_div_pos - old_div_pos) % self.divisions
        clockwise_distance = (old_div_pos - next_div_pos) % self.divisions

        reverse = anti_clockwise_distance < clockwise_distance ## reverse = True = rotate anti_clockwise
        angle = (anti_clockwise_distance if reverse else clockwise_distance) * (360 / self.divisions)

        return angle, reverse


    def rotate(self):
        try:
            angle, reverse = self.get_rotate_direction()

            print("Angle is: " + str(angle), reverse)
            print(reverse)
            self.motor.rotate_by(angle, reverse)

            # disable the motor to conserve energy
        except:
            print("An error occured in the rotate method of platform")

    # def rotateCCW(self, angle):
    #     if AUTOMATION:
    #         data = {'angle':360//self.divisions, 'division':self.divisions, 'rotate':angle}
    #         self.platform.write(f"{data}\n")
    #     else:
    #         self.motor.rotate_by(abs(angle), reverse=True)

    # def rotateCW(self, angle):
    #     if AUTOMATION:
    #         data = {'angle':360//self.divisions, 'division':self.divisions, 'rotate':angle}
    #         self.platform.write(f"{data}\n")
    #     else:
    #         self.motor.rotate_by(angle)

    def close_curtain():
        pass

    def open_curtain():
        pass

    def open_curtain_to(width):
        pass

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


if __name__ == "__main__":
    # Create the state machine
    fsm = StateMachine(4)

    async def main():
        set_global_exception()
        while True:
            await fsm.update()
            await asyncio.sleep(1)


    try:
        asyncio.run(main())
    finally:
        # fsm.delay.stop() #stop the timer
        asyncio.new_event_loop()  # Clear retained state
