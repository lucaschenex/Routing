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
        # key: dest; value = [(distance, port),(. . .),(. . .)]
        self.route = {}
        # key: dest; value: (next_hop_through_port, min_distance)
        self.forward = {}
        # key: port; value: neighbor
        self.dict = {}
        
    def cal_min (self, op):
        assert(len(op) > 0), "invalid entry number"
        op.sort()
        return op[0];
    
    def compute (self, table):
        output = {}
        for key in table.keys():
            output[key] = self.cal_min(table[key])
        return output
    
    
    def handle_rx (self, packet, port):
        # Add your code here!
        if packet.__class__.__name__ == "DiscoveryPacket":
            if packet.is_link_up:
                if packet.src in self.route:
                    self.route[packet.src].append((1, port))
                else:
                    self.route[packet.src] = [(1, port)]
                self.dict[port] = packet.src
            else:
                del self.dict[port]
                for key in self.route:
                    for v in self.route[key]:
                        if v[1] == packet.src:
                            self.route[key].remove(v)
                        if not len(self.route[key]):
                            del self.route [key]
                            
            self.forward = self.compute(self.route)
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
            
            # implicit withdraw
            for d in self.route:
                if d not in dests:
                    for v in self.route[d]:
                        if v[1] == packet.src:
                            self.route[d].remove(v)
            
            for d in dests:
                if d == self:
                    pass
                else:
                    # if new destination requires update
                    # flag indicating whether the routing table has changed
                    if d not in self.route.keys():
                        self.route[d] = [(port, packet.get_distance(d) + 1)]
                        flag = True
                    else:
                        # what if route has two options with the same cost?
                        new_value = packet.get_distance(d) + 1;
                        not_found = True
                        for v in self.route[d]:
                            if v[1] == port:
                                if v[0] != new_value:
#                                    v[0] = new_value
                                    v = (new_value, v[1])
                                    flag = True
                                not_found = False
                        if not_found:
                            self.route[d].append((port, packet.get_distance(d) + 1))
                            self.forward = self.compute(self.route)
                            flag = True
                            
            if flag:
                # poison reverse, send poison reverse to neighbors only when self decides to send packets through that neighbor.
                for pt in self.dict.keys():
                    update = RoutingUpdate()
                    for d in self.forward.keys():
                        if pt == self.forward[d][0]:
                            update.add_destination(d, 100)
                        else:
                            update.add_destination(d, self.forward[d][1])
                    self.send(update, pt, flood = False)            
                                
        else:
            if packet.dst == self:
                pass
            else:
                self.send(packet,self.forward[packet.dst][0], flood = False)


