class Condition:
    curtain_done_state = True

    @classmethod
    def get_curtain_done_state(cls):
        value = cls.curtain_done_state

        if value:
            cls.curtain_done_state = False

        return value
    
    @classmethod
    def change_curtain_done_state(cls, state=False):
        cls.curtain_done_state = state
