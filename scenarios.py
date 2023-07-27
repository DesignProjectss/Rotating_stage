from collections import OrderedDict

STATES = OrderedDict([
            (
                'Scene_0',
                    
                    {
                        'on_enter':[],
                        'on_exit':['curtain.Curtain.draw']

                    }
            ),
    
            (
                
                'Scene_1',
                    
                    {
                        'on_enter':['lamp.Lamp.fade_out',
                                    'curtain.Curtain.draw'
                              ],
                        'on_exit':['lamp.Lamp.fade_in',
                                   'curtain.Curtain.close']

                    }

            ),

            (
                'Scene_2',

                    {
                        'on_enter':['lamp.Lamp.fade_out',
                                    'curtain.Curtain.draw'
                              ],
                        
                        'on_exit':['lamp.Lamp.fade_in',
                                   'curtain.Curtain.close']

                    }



            ),

            (
                'Scene_3',

                    {
                        'on_enter':['lamp.Lamp.fade_out',
                                    'curtain.Curtain.draw'
                              ],
                        
                        'on_exit':['lamp.Lamp.fade_in',
                                   'curtain.Curtain.close']

                    }



            ),

            (
                'Scene_4',

                    {
                        'on_enter':['lamp.Lamp.fade_out',
                                    'curtain.Curtain.draw'
                              ],
                        
                        'on_exit':['lamp.Lamp.fade_in',
                                   'curtain.Curtain.close']

                    }



            )

])

TRANSITIONS = OrderedDict([
            (
                'Scene_1', 
                    {
                        'transition_time': 10000,
                        'prepare': [],
                        'unless': [],
                        'before': [],
                        'after': {'lamp.Lamp.flicker': '10'},
                        'conditions': [],
                        'on_enter': [],
                        'on_exit': []
                        #'condition': [{'audio.listen_for_cues':20}], #wait for the event to happen before eventually transitioning: future considerations
                        
                    }
                
            ),
    
            (
                'Scene_3', 
                    {
                        'transition_time': 20000,
                        'prepare': [],
                        'unless': [],
                        'before': [],
                        'after': {'lamp.Lamp.flicker': '10'},
                        'conditions': [],
                        'on_enter': [],
                        'on_exit': []
                        
                    }
                
                
            ),
    
            (
                'Scene_2', 
                    {
                        'transition_time': 5000,
                        'prepare': [],
                        'unless': [],
                        'before': [],
                        'after': {'lamp.Lamp.flicker': 10},
                        'conditions': [],
                        'on_enter': [],
                        'on_exit': []
                        
                    }
                
                
            ),
            
            (
                'Scene_4', 
                    {
                        'transition_time': 10000,
                        'prepare': [],
                        'unless': [],
                        'before': [],
                        'after': {'lamp.Lamp.flicker': 10},
                        'conditions': [],
                        'on_enter': [],
                        'on_exit': []
                        
                    }
            ),
            (
                'Scene_0', 
                    {
                        'transition_time': 0,
                        'prepare': [],
                        'unless': [],
                        'before': ['lamp.Lamp.off'],
                        'after': {'shut_down': 10},
                        'conditions': [],
                        'on_enter': [],
                        'on_exit': []
                    }

            )

])



PINS = OrderedDict([
    (
        #"GPIO_POOL",
        #[0,2,3,4,5,12,13,14,15,18,19,21,22,23,25,26,27,32,33]# for esp32 38 pin config
        "GPIO_POOL",
        [13,14,12,27,33,26,15,4,18,23,22,25] #for esp32 30 pin config

    )


])
