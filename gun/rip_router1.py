from sim.api import *
from sim.basics import *

'''
Create your RIP router in this file.
'''
class RIPRouter (Entity):
    def __init__(self):
        self.routing_table = dict()    # key:destination, value:dict: key:next node, value:cost
        self.forwarding_table=dict()   # key:dest, value: (port,cost)
        self.neighbours = dict()       # key:neighbour, value: port
        self.ports = dict()            # key:port, value:neighbour

    def handle_rx (self, packet, port):
        if isinstance(packet,DiscoveryPacket):
            self.update(packet,port)
        elif isinstance(packet,RoutingUpdate):
            self.update2(packet,port)       
        elif packet.dst != self and packet.ttl != 0:
            self.send(packet,self.forwording_table[packet.dst])
        a = 1
            
    def update(self,discovery_packet,port): # dealing with link fail or come up
        if discovery_packet.is_link_up:
            source = discovery_packet.src
            if source not in self.routing_table:
                self.routing_table[source] = dict()
            self.routing_table[source][source] = 1
            self.ports[port] = source
            self.neighbours[source] = port
            if source in self.forwarding_table:
                self.update_shortest_distance_and_port(source)
            else:
                self.forwarding_table[source] = (port,1)
        else:
            neighbour = self.ports[port]
            del self.neighbours[neighbour]
            del self.ports[port]
            for dest in self.routing_table.keys():
                if neighbour in self.routing_table[dest]:
                    del self.routing_table[dest][neighbour]
                if self.forwarding_table[dest][0] == port:
                    self.update_shortest_distance_and_port(dest)
        self.send_update_info()
            
    def update_shortest_distance_and_port(self,dest):
        first_iter = True
        result_distance,result_port = None, None
        routes = self.routing_table[dest]
        for next_hop in routes.keys():
            if first_iter:
                result_distance = routes[next_hop]
                result_port = self.neighbours[next_hop]
                first_iter = False
            elif result_distance > routes[next_hop] or (result_distance == routes[next_hop] and self.neighbours[next_hop] < result_port):
                result_distance = routes[next_hop]
                result_port = self.neighbours[next_hop]                       
        if result_distance == None and result_port == None:     #if no neighbour can access to the dest, dest is access for this node as well
            del self.routing_table[dest]
            del self.forwarding_table[dest]
        else:                                   #update the new shortest distance and the corresponding port
            self.forwarding_table[dest] = (result_port,result_distance)
                            
    def update2(self,packet,port):     # dealing with incoming distance vector
        boolean_of_change = False
        source = packet.src
        print "update2!"
        print "Iam: %s, and source is %s",repr(self),repr(source)
        print "The information is:",packet.paths

        for dest in self.routing_table.keys():
            if source!= dest and source in self.routing_table[dest] and dest not in packet.paths:
                del self.routing_table[dest][source]
                if self.forwarding_table[dest][0] == port:
                    forwarding_info = self.forwarding_table[dest]
                    self.update_shortest_distance_and_port(dest)
                    if dest in self.forwarding_table and forwarding_info != self.forwarding_table[dest]:
                        boolean_of_change = True

        link_cost_to_src = self.routing_table[source][source]
        for dest in packet.all_dests():
            cost_to_dest = link_cost_to_src + packet.get_distance(dest)
            if dest not in self.routing_table:
                self.routing_table[dest] = dict()
                self.routing_table[dest][source] = cost_to_dest
                self.forwarding_table[dest] = (port,cost_to_dest)
                boolean_of_change = True
            elif source not in self.routing_table[dest] or self.routing_table[dest][source] != cost_to_dest:
                self.routing_table[dest][source] = cost_to_dest
                self.update_shortest_distance_and_port(dest)
                boolean_of_change = True

        print "and not my forwarding_table is:", self.forwarding_table

        if boolean_of_change:
            self.send_update_info()

    def send_update_info(self,port=None):
        for port_ in self.ports:
            if port != port_:
                update_packet = self.make_update_packet(port_)
                self.send(update_packet,port_)

    def make_update_packet(self,port):
        packet = RoutingUpdate()
        neighbour = self.ports[port]
        for dest in self.forwarding_table.keys():
            if dest != neighbour:
                if self.forwarding_table[dest][0] == port:    # poison reverse
                    packet.add_destination(dest,100)
                else:
                    packet.add_destination(dest,self.forwarding_table[dest][1])
        packet.src, packet.dst, packet.ttl = self, neighbour, 20
        return packet
        
