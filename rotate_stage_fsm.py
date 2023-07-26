
#from micropython import const
from machine import Pin
import sys
from collections import OrderedDict
import uasyncio as asyncio
from machine import RTC
import ntptime

from delay_ms import Delay_ms
import ulogger

from config import TRANSITIONS, STATES, PINS
from motor import Motor

class Clock(ulogger.BaseClock):
    def __init__(self):
        self.rtc = RTC()
        ntptime.host = "ntp.ntsc.ac.cn"
        #ntptime.settime()

    def __call__(self) -> str:
        y,m,d,_,h,mi,s,_ = self.rtc.datetime ()
        return '%d-%d-%d %d:%d:%d' % (y,m,d,h,mi,s)
    
clock = Clock()

handlers = (
    ulogger.Handler(
        level=ulogger.INFO,
        colorful=True,
        fmt="&(time)% - &(level)% - &(name)% - &(fnname)% - &(msg)%",
        clock=clock,
        direction=ulogger.TO_TERM,
    ),
    ulogger.Handler(
        level=ulogger.ERROR,
        fmt="&(time)% - &(level)% - &(name)% - &(fnname)% - &(msg)%",
        clock=clock,
        direction=ulogger.TO_FILE,
        file_name="logging.log",
        max_file_size=2048 # max for 2k
    )
)

_LOGGER = ulogger.Logger(__name__, handlers)


class Condition(object):
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


class Transition(object):
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
                 after=None, prepare=None):
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

        self.prepare = [self._check_source_dest]
        self.before = [self._check_allowed_states]
        self.after = []

        self.conditions = []
        if conditions is not None:
            for cond in listify(conditions):
                self.conditions.append(self.condition_cls(cond))
        if unless is not None:
            for cond in listify(unless):
                self.conditions.append(self.condition_cls(cond, target=False))

    def _eval_conditions(self, machine):
        for cond in self.conditions:
            if not cond.check(machine):
                _LOGGER.debug("%s Transition condition failed: %s() does not return %s. Transition halted.",
                              machine.name, cond.func, cond.target)
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
        _LOGGER.debug("{} Executed callbacks before conditions.".format(self.model.name, machine.name))

        if not self._eval_conditions(machine):
            return False

        machine.callbacks(self.before)
        _LOGGER.debug("{} Executed callback before transition.".format(self.model.name, machine.name))

        if self.dest:  # if self.dest is None this is an internal transition with no actual state change
            self._change_state(machine)

        machine.callbacks(self.after)
        _LOGGER.debug("{} Executed callback after transition.".format(self.model.name, machine.name))
        return True

    def _change_state(self, machine):
        machine.go_to_state(self.model, self.dest)

    def _check_source_dest(self):
        if self.source == self.dest:
            self.dest = None

    def _check_allowed_states(self):
        if not self.dest in STATES.keys():
            self.dest = None

    def add_callback(self, trigger, func):
        """ Add a new before, after, or prepare callback.
        Args:
            trigger (str): The type of triggering event. Must be one of
                'before', 'after' or 'prepare'.
            func (str or callable): The name of the callback function or a callable.
        """
        callback_list = getattr(self, trigger)
        callback_list.append(func)

    def __repr__(self):
        return "<%s('%s', '%s')@%s>" % (type(self).__name__,
                                        self.model.state.name, self.dest, id(self))

#abstract state base class
class State(object):

    def __init__(self, name, location):
        self.name = name
        self.location = location

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def location(self):
        return self._location
    
    @location.setter
    def location(self, value):
        self._location = value

    def enter(self, machine):
        _LOGGER.info("Entering state {}".format(machine.model.current_state.name))
        
        machine.model.rotate()
        #read actions to be taken from STATE
        for fn in STATES[self.name]['on_enter']:
            if isinstance(fn, dict): # it contains the fn name as key and args as values
                fn_name, fn_args = fn.items()
                cls_name, met_name = fn_name.split('_', 1)
                getattr(cls_name, met_name)(fn_args) # make sure the fn takes *args and **kwargs
            elif isinstance(fn, str):
                fn_name, fn_args = fn.items()
                cls_name, met_name = fn_name.split('_', 1)
                getattr(cls_name, met_name)() # make sure the fn takes *args and **kwargs
        
        

    def exit(self, machine):
        _LOGGER.info("Exiting state {}".format(machine.model.current_state.name))
        
        machine.model.close_curtain()
        #read actions to be taken from STATE
        for fn in STATES[self.name]['on_exit']:
            if isinstance(fn, dict): # it contains the fn name as key and args as values
                fn_name, fn_args = fn.items()
                cls_name, met_name = fn_name.split('_', 1)
                getattr(cls_name, met_name)(fn_args) # make sure the fn takes *args and **kwargs
            elif isinstance(fn, str):
                fn_name, fn_args = fn.items()
                cls_name, met_name = fn_name.split('_', 1)
                getattr(cls_name, met_name)() # make sure the fn takes *args and **kwargs
        

    def update(self, machine): #runs updates globally for all states entered
        pass

#state machine class
class StateMachine(object):

    name = 'Platform Rotation System'

    transition_cls = Transition

    delay = Delay_ms()

    gpios = PINS['GPIO_POOL']
    
    divisions = len(STATES)
    
    def __init__(self):
                
        self.model = Platform(self.divisions)
        
        self.delay.callback(self._run_transitions, ()) #register the callback with the timer
        
        self.transitions_time = 0

        self.transition_generator = self._create_transition()
        
        self.transition = next(self.transition_generator)
        
        self.delay.trigger(self.transitions_time) #transition immediately

    @staticmethod
    def _add_pins(model, states, number_of_bulbs):
        for pin, state_name in enumerate(states[:number_of_bulbs]):
            #print(StateMachine.gpios[pin])
            model.gpios[state_name.split('_')[0]] = Pin(StateMachine.gpios[pin], Pin.OUT)
        del StateMachine.gpios[:number_of_bulbs]

    @classmethod
    def _create_transition(cls):
        for i in range(len(TRANSITIONS)):
            trans = TRANSITIONS.popitem(False)
            
            state_name = trans[0]
            
            self.transition_time = trans[1]['transition_time']
            conditions = trans[1]['conditions']
            unless = trans[1]['unless']
            before = trans[1]['before']
            after = trans[1]['after']
            prepare = trans[1]['prepare']
            
            yield cls.transition_cls(self, conditions, unless, before, after, prepare)
        

    def _run_transitions(self):
        self.transition.execute(self)
        _LOGGER.info(f"There will be transition in: {self.transition_time}ms")
        
        try:
            self.transition = next(self.transition_generator)
        except StopIteration:
            pass # kill the machine or something
        
        self.delay.trigger(self.transition_time) #when is the next transition?

    def go_to_state(self, state_name):
        if self.model.current_state:
            _LOGGER.debug('Exiting {}'.format(self.model.current_state.name))
            self.model.old_state = self.model.current_state
            self.model.current_state.exit(self)
            
        self.model.current_state = self.model.states[state_name] 
        _LOGGER.debug('Entering {}'.format(self.model.current_state.name))
        self.model.current_state.enter(self)# the machine instance has been passed in

    async def update(self):
        await asyncio.sleep_ms(1)
        self.model.state.update(self)


class Platform():

    def __init__(self, divisions):
        self.divisions = divisions
        self.motor = Motor()
        self.old_state = State(name='Scene_0', location=0)
        self.current_state = None
        self.states = {}
        self.locations = {2: [90, 270], 3: [45, 135, 270], 4: [45, 135, 225, 315]}

        for i in range(1, divisions+1):
            locations = self.locations[divisions]
            self.states[f'Scene_{i}'] = State(name=f'Scene_{i}', location=locations[i])
                        
    @property
    def divisions(self):
        return self._divisions
    
    @divisions.setter
    def divisions(self, value):
        # divisions can only take a value from 2,3 and 4. 
        if value not in [2,3,4]:
            raise ValueError("divisions can only take any value from 2,3 and 4")
        self._divisions = value
        
    def calibrate(self, reverse=False): # Just to set our motor to first division(state 1) facing us
        self.motor.move_one_step(reverse)
    
    def rotate(self):
        location_diff = self.current_state.location - self.old_state.location
        if abs(location_diff) > 180: #find the shortest path for energy conservation
            # self.rotateCCW(location_diff)
            self.motor.rotate_by(location_diff, reverse=True)
        else:
            self.motor.rotate_by(location_diff)
            # self.rotateCW(location_diff)
            
        # disable the motor to conserve energy
    
    # def rotateCCW(self):
    #     pass

    # def rotateCW(self):
    #     pass
    
    def close_curtain():
        pass
    
    def open_curtain():
        pass
    
    def open_curtain_to(width):
        pass
    

class Lamps():

    def __init__(self):
        pass
    

def set_global_exception():
    def handle_exception(loop, context):
        import sys
        sys.print_exception(context["exception"])
        sys.exit()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(handle_exception)


# Create the state machine
fsm = StateMachine()


async def main():
    set_global_exception()
    while True:
        #print('in main...')
        await fsm.update()
        await asyncio.sleep(1)


try:
    asyncio.run(main())
except:
    fsm.delay.stop() #stop the timer
    asyncio.new_event_loop()  # Clear retained state