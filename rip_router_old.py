from sim.api import *
from sim.basics import *

'''
Create your RIP router in this file.
Yanming & Beidi 
Oct15 15:06
'''
class RIPRouter (Entity):
    def __init__(self):
        """
        forwarding table is a dictionary, its key is the possible out_going path(port) it can choose, in other words, first row of the table; its value is a tuple containing the destination and the cost going from one particular port
        """
        # Add your code here!
        # key: dest; value: (distance, port)
        self.forward = {}
        # key: port; value: neighbor
        self.dict = {}
        
    def handle_rx (self, packet, port):
        # Add your code here!
        if packet.__class__.__name__ == "DiscoveryPacket":
            if packet.is_link_up:
                self.forward[packet.src] = (port, 1)
                self.dict[port] = packet.src
            else:
                self.forward[packet.src] = (port, 100)
                self.dict[port] = packet.src
                
            update = RoutingUpdate()
            for d in self.forward.keys():
                update.add_destination(d, self.forward[d][1])
            for pt in self.dict.keys():
                if pt != port:
                    self.send(update, pt, flood = False)
            
        elif packet.__class__.__name__ == "RoutingUpdate":
            dests = packet.all_dests()
            source = packet.src
            flag = False
            for d in dests:
                if d == self:
                    pass
                else:
                    neighbor = self.dict[port]
                    distance = self.forward[neighbor][1]
                    
                    if d not in self.forward.keys():
                        self.forward[d] = (port, distance + packet.get_distance(d))
                        flag = True
                    else:
                        origin = self.forward[d][1]
                        value = packet.get_distance[d] + distance
                        if origin == value:
                            ori_port = self.forward[d][0]
                            if ori_port > port:
                                self.forward[d][0] = port
                                flag = True
                        elif origin > value:
                            self.forward[d] = (port, value)
                            flag = True
            if flag:
                update = RoutingUpdate()
                for d in self.forward.keys():
                    update.add_destination(d, self.forward[d][1])
                for pt in self.dict.keys():
                    if pt != port:
                        self.send(update, pt, flood = False)
                                
        else:
            if packet.dst == self:
                pass
            else:
                self.send(packet,self.forward[packet.dst][0], flood = False)


