from collections import OrderedDict

STATES = OrderedDict([
            (
                'Scene_1',
                    
                    {
                        'on_enter':['light_fade_in', 
                                   'light_fade_out',
                                   'animal_sound'
                                  ],
                        'on_exit':['draw_curtain']

                    }

            ),

            (
                'Scene_2',

                    {
                        'on_enter':['light_fade_in', 
                                       'light_fade_out',
                                       'animal_sound'
                                      ],
                        'on_exit':['draw_curtain']
                    }


            ),

            (
                'Scene_3',

                    {
                        'on_enter':['light_fade_in', 
                                       'light_fade_out',
                                       'animal_sound'
                                      ],
                        'on_exit':['draw_curtain']
                    }


            ),

            (
                'Scene_4',

                    {
                        'on_enter':['light_fade_in', 
                                       'light_fade_out',
                                       'animal_sound'
                                      ],
                        'on_exit':['draw_curtain']
                    }


            )

])

TRANSITIONS = OrderedDict([
            (
                'Scene_1', 
                    {
                        'transition_time': 5,
                        'prepare': [],
                        'unless': []
                        'before': ['draw_curtain'],
                        'after': {'10':'flicker_light'}, # should be a list - check add_callback method
                        'condition': [{'listen_for_cues':20}], #wait for the event to happen before eventually transitioning
                        
                    }
                
            ),
    
            (
                
                
            ),
    
            (
                
                
            ),

])



PINS = OrderedDict([
    (
        #"GPIO_POOL",
        #[0,2,3,4,5,12,13,14,15,18,19,21,22,23,25,26,27,32,33]# for esp32 38 pin config
        "GPIO_POOL",
        [13,14,12,27,33,26,15,4,18,23,22,25] #for esp32 30 pin config

    )


])
