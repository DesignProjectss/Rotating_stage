
class MyCondition:
   def __init__(self):

       self.audio_cue= True
       self.btn_press= True


   def myboolean(self):
       if self.audio_cue:
           return True

       elif self.btn_press:
           return True

       else:
           return False

