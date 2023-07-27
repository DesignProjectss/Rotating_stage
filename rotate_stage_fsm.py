
#from micropython import const
# from machine import Pin
import sys
from collections import OrderedDict
import uasyncio as asyncio
import ntptime

from delay_ms import Delay_ms

import os

from motor import Motor

if os.name != 'posix':
    from primitives import Delay_ms, Semaphore
    from machine import RTC
    import ulogger
    
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
# except ImportError:
#     pass


from scenarios import TRANSITIONS, STATES, PINS


AUTOMATION = True

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

        self.prepare = [self._check_source_dest]
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
                #_LOGGER.debug("%s Transition condition failed: %s() does not return %s. Transition halted.",machine.name, cond.func, cond.target)
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
        #_LOGGER.debug("{} Executed callbacks before conditions.".format(machine.name))

        if not self._eval_conditions(machine):
            return False

        machine.callbacks(self.before)
        #_LOGGER.debug("{} Executed callback before transition.".format(machine.name))

        if self.dest:  # if self.dest is None this is an internal transition with no actual state change
            self._change_state(machine)

        machine.callbacks(self.after)
        #_LOGGER.debug("{} Executed callback after transition.".format(machine.name))
        # print(machine.model.current_state.name)
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

    def add_callback(self, trigger, func):
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
            
            
    def add_state_callback(self, machine, trigger, func):
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

#abstract state base class
class State(object):

    def __init__(self, name, location):
        self.name = name
        self.location = location
        self.on_enter = STATES[self.name]['on_enter']
        self.on_exit = STATES[self.name]['on_exit']

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
        #_LOGGER.info("Entering state {}".format(machine.model.current_state.name))
        
        # machine.model.rotate()
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
        #_LOGGER.info("Exiting state {}".format(machine.model.current_state.name))
        
        # machine.model.close_curtain()
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

    
class Platform():

    def __init__(self, divisions):
        self.divisions = divisions
        self.motor = Motor()
        self.old_state = None #State(name='Scene_0', location=0)
        self.current_state = State(name='Scene_0', location=0) #None
        self.states = {}
        # self.locations = {2: [90, 270], 3: [45, 135, 270], 4: [45, 135, 225, 315]}
        self.locations = [(360//int(self.divisions))*i for i in range(1,int(self.divisions)+1)]
        
        self.locations.insert(0, 0)
        
        print(self.locations) #added the dummy Scene_0
        
        for i in range(0, self.divisions+1): 
            self.states[f'Scene_{i}'] = State(name=f'Scene_{i}', location=self.locations[i])
            
        if AUTOMATION:
            import serial
            self.platform = serial.Serial('/dev/pts/2',115200) #remember to change the port number
            
        self.start_motor()
            
    def start_motor(self):
        pass
                        
    @property
    def divisions(self):
        return self._divisions
    
    @divisions.setter
    def divisions(self, value):
        # divisions can only take a value from 2,3 and 4. 
        if value not in [2,3,4]:
            raise ValueError("divisions can only take any value from 2,3 and 4")
        self._divisions = value

    def calibrate(self, reverse):
        self.motor.move_one_step(reverse)

    def rotate(self):
        # print([state.location for state in self.states.values()])
        print(self.current_state.location, self.old_state.location)
        location_diff = self.current_state.location - self.old_state.location
        print(location_diff)
        if abs(location_diff) > 180: #find the shortest path for energy conservation
            self.rotateCCW(location_diff)
        else:
            self.rotateCW(location_diff)
            
        # disable the motor to conserve energy
    
    def rotateCCW(self, diff):
        if AUTOMATION:
            data = {'angle':360//self.divisions, 'division':self.divisions, 'rotate':diff}
            self.platform.write(f"{data}\n")
        else:
            self.motor.rotate_by(abs(diff), reverse=True)
            
    def rotateCW(self, diff):
        if AUTOMATION:
            data = {'angle':360//self.divisions, 'division':self.divisions, 'rotate':diff}
            self.platform.write(f"{data}\n")
        else:
            self.motor.rotate_by(diff)
    
#state machine class
class StateMachine(object):

    name = 'Platform Rotation System'

    transition_cls = Transition
    
    # model = Platform

    gpios = PINS['GPIO_POOL']
    
    divisions = len(STATES)
    
    def __init__(self, plat_div):
                
        self.model = Platform(plat_div)
        
        self.delay = Delay_ms(self._run_transitions, ())
                        
        self.transition_generator = self._create_transition()
        
        self.transition_time, self.transition = next(self.transition_generator)
        
        print(self.transition_time)
        
        print(self.transition)
        
        self.delay.trigger(self.transition_time)

    @staticmethod
    def _add_pins(model, states, number_of_bulbs):
        for pin, state_name in enumerate(states[:number_of_bulbs]):
            #print(StateMachine.gpios[pin])
            model.gpios[state_name.split('_')[0]] = Pin(StateMachine.gpios[pin], Pin.OUT)
        del StateMachine.gpios[:number_of_bulbs]

    # @classmethod
    def _create_transition(self):
        for key in TRANSITIONS.keys():
            trans = TRANSITIONS.get(key)
            
            state_name = key
            
            transition_time = trans['transition_time']
            
            #for conditions and unless to work, we might need to consider the use of an asyn queue instead of generator.
            conditions = trans['conditions']
            unless = trans['unless']
            
            before = trans['before']
            after = trans['after']
            prepare = trans['prepare']
            
            on_enter = trans['on_enter']
            on_exit = trans['on_exit']
            
            yield transition_time, self.transition_cls(self.model.current_state.name, state_name, conditions, unless, before, after, prepare, on_enter, on_exit) # how to put an obj back into the generator in the case a condition fails?  Use the queue instead

    def _run_transitions(self):
        condition = self.transition.execute(self)
        #_LOGGER.info(f"There will be transition in: {self.transition_time}ms")
        if condition:
            try:
                self.transition_time, self.transition = next(self.transition_generator)
                print(self.transition_time)
                print(self.transition)
                self.delay.trigger(self.transition_time)
            except StopIteration:
                self.delay.stop() # kill the machine or something
        else:
            self.trigger(5000) # in case the condition fails, try it again every 5 mins until it passes.
        
    def go_to_state(self, state_name):
        if self.model.current_state:
            #_LOGGER.debug('Exiting {}'.format(self.model.current_state.name))
            self.model.old_state = self.model.current_state
            self.model.current_state.exit(self)
            
        self.model.current_state = self.model.states[state_name] 
        #_LOGGER.debug('Entering {}'.format(self.model.current_state.name))
        self.model.current_state.enter(self)# the machine instance has been passed in
        
    def callbacks(self, funcs):
        """ Triggers a list of callbacks """
        for func in funcs:
            self.callback(func)
            #_LOGGER.info("%sExecuted callback '%s'", self.name, func)

    def callback(self, func):
        """ Trigger a callback function with passed event_data parameters. In case func is a string,
            the callable will be resolved from the passed model in event_data. This function is not intended to
            be called directly but through state and transition callback definitions.
        Args:
            func (str or callable): The callback function.
                1. First, if the func is callable, just call it
                2. Second, we try to import string assuming it is a path to a func
                3. Fallback to a model attribute
            data: arguments
        """
        if isinstance(func, dict): # it contains the fn name as key and args as values
            func, fn_args = fn.items()
            func = self.resolve_callable(func)
            func(fn_args)
        else:   
            func = self.resolve_callable(func)
            func()
        # if self.send_event:
        #     func(event_data)
        # else:
        #     func(*event_data.args, **event_data.kwargs)

    @staticmethod
    def resolve_callable(func):
        """ Converts a model's property name, method name or a path to a callable into a callable.
            If func is not a string it will be returned unaltered.
        Args:
            func (str or callable): Property name, method name or a path to a callable
        Returns:
            callable function resolved from string or func
        """
        if isinstance(func, str):
            # try:
            #     func = getattr(event_data.model, func)
            #     if not callable(func):  # if a property or some other not callable attribute was passed
            #         def func_wrapper(*_, **__):  # properties cannot process parameters
            #             return func
            #         return func_wrapper
            # except AttributeError:
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
        
    # async def run_delay_timer(self, time, sema):
    #     async with sema:
    #         await asyncio.sleep_ms(time)
    #         self._run_transitions()
        

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
        # sema = Semaphore()
        # for time in [val['transition_time'] for val in TRANSITIONS.values()]:
        #     asyncio.create_task(fsm.run_delay_timer(time, sema))
        while True:
            #print('in main...')
            await fsm.update()
            await asyncio.sleep(1)


    try:
        asyncio.run(main())
    finally:
        # fsm.delay.stop() #stop the timer
        asyncio.new_event_loop()  # Clear retained state