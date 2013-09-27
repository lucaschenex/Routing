from sim.api import *
from sim.basics import *

'''
Link-State Routing Protocol
Yanming Chen & Beidi Chen
UC Berkeley
15:06 Oct15 2012
'''

class LSRouter (Entity):
    def __init__(self):
        self.global_view = dict()
        
        self.map = dict()
        
    def djkstra(self, graph, source, target):
        dist = {}
        previous = {}
        for elem in graph:
            dist[elem] = 100000
            previous[elem] = None
        dist[source] = 0  
        newGraph = graph.copy()
        while len(newGraph.keys())!=0:
            w = dist.values().sort()
            u = w[0]
            if u==target:
                break
            del newGraph[u]
            if dist[u]==100000:
                break
            
            for v in graph[u]:
                alt = dist[u]+1
                if alt< dist[v]:
                    dist[v] = alt
                    previous[v] = u
                    
        while True:
            if not len(previous):
                break
            target = previous[target]
            if previous[target]==source:
                return target
    
    
    
    def identical_with_forward(self, origin_table):
        identical = True
        if len(origin_table) != self.forward:
            identical = False
        elif origin_table.keys() != self.forward.keys():
            identical = False
        else:
            for key in origin_table:
                if origin_table[key] != self.forward[key]:
                    identical = False
                    break
        return identical
    
    def handle_rx (self, packet, port):
        if packet.__class__.__name__ == "ChangeNotification":
            if packet.is_link_up:
                self.map[port] = packet.src
                if packet.src not in self.global_view[self]:
                    self.global_view[self] = [packet.src]
                else: # packet.src in self.global_view[self]
                    self.global_view[self].append(packet.src)
        for pt in self.map:
            update = RoutingFlood()
            update.set_vision(self.global_view)
            update.ttl = 20
            self.send(RoutingFlood, pt, flood = True)
            
                                                        
        elif packet.__class__.__name__ == "RoutingFlood":
            self.global_view = packet.get_vision()
            
      
        else:
            if packet.dst != self and packet.ttl != 0:
                next_node = self.djkstra(self.global_view, self, packet.dst)
                for p in self.map():
                    if self.map[p] = next_node:
                        outgoing = p
                        break
                self.send(packet, outgoing, flood = False)
    