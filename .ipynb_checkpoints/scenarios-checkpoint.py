from collections import OrderedDict

SCENARIOS = OrderedDict([
            (
                'Scene_1',
                    [
                        {
                            'initial_state': True, #this can be derived from the dividers
                            'transition_time':10,
                            'effects_on_enter':['light_fade_in', 
                                       'light_fade_out',
                                       'animal_sound'
                                      ],
                            'effects_on_exit':['draw_curtain'],
                            'effects_after': {'10':'flicker_light'},
                            'transition_event': 'listen_for_cues',
                            'priority': ['transition_event', 'transition_time'],
                            'response_speed': 'standard'
                            'record': ['video', 'audio']
                        
                        }
                    ]
            ),

            (
                'Scene_2',

                    {
                        'initial_state': False
                    }


            ),

            (
                'Scene_3',

                    {
                        'initial_state': False
                    }


            ),

            (
                'Scene_4',

                    {
                        'initial_state': False
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
