from sim.api import *
from sim.basics import *

'''
Create your learning switch in this file.
'''
class LearningSwitch(Entity):
    def __init__(self):
        # Add your code here!
        self.dict = {}


    def handle_rx (self, packet, port):
        # Add your code here!
        self.dict[packet.src] = port
        if packet.dst==self:
            pass
        elif packet.dst in self.dict:
            self.send(packet,self.dict[packet.dst], flood = False)
        else:
            self.send(packet, port, flood = True)
