#Please run in Python 2

import socket
import sys
import time
import os
from collections import defaultdict
import threading
from threading import Thread
import socket

#Class to store the router info and who it's neighbours are
class Router:
    def __init__(self, ID, port_no):
        self.ID = ID
        self.port = port_no
        self.neighs = []

    def add_neighbour(self, target_router, cost):
        router = Neighbour(target_router, cost)
        self.neighs.append(router)

#Neighbour class stores the IDs and cost to the neighbours
class Neighbour:
    def __init__(self, target_router, cost):
        self.target_router = target_router
        self.cost = cost


def sort_input_file(file):
    list = file.split("\n")
    initial_router = Router(list[0][0], list[0][2:])
    num_of_neighbours = int(list[1])
    neighbours = set()
    #This will loop through all the neighbour info
    for i in range(2, num_of_neighbours+2):
        data = list[i].split(" ")
        neighbours.add(data[0])
        neighbour = Router(data[0], int(data[2]))
        initial_router.add_neighbour(neighbour, float(data[1]))
    return (initial_router, neighbours)


#We'll broadcast in the exact same format as the file we got
#This way we can utilise our sort_input_file() function each time
def broadcast(router):
    while True:
        packet = "%s %s\n" %(str(router.ID), str(router.port))
        packet += "%s\n" %str(len(router.neighs))
        for neighbour in router.neighs:
            packet += "%s %s %s\n" %(neighbour.target_router.ID, str(neighbour.cost), str(neighbour.target_router.port))
        #Removing the empty line at the end created by the loop
        packet = packet[:-1]
        for neighbour in router.neighs:
            socket.sendto(packet, ("localhost", neighbour.target_router.port))
        time.sleep(1)

    #We gotta thread stuff later

#Arguments are the class 'initial_router' and list of all routers that are alive
#Returns: cost to each living neighbour
#Returns: Map of previously traversed router
def dijkstra(initial_router, known_routers):
    all_routers = [initial_router.ID]
    visited = []
    cost = {initial_router.ID:0}
    previous = {initial_router.ID:initial_router.ID}
    while True:
        best_route = None
        for router in all_routers:
            if best_route is None or cost[router] < best_route:
                best_route = cost[router]
                current_router = router
        #We cycle through the routers. Works well if there aren't a tonne
        #otherwise it'll take too long
        if len(all_routers) == 0:
            break
        all_routers.remove(current_router)

        no_routers = 0
        #Now we get info from our list of routers
        for n in known_routers:
            if n.ID == current_router:
                best_router = n
                break
            no_routers += 1
        if no_routers == len(known_routers): #if destination isn't in active known_routers
            continue


        visited.append(best_router.ID)
        for n in best_router.neighs:
            neigh_ID = n.target_router.ID
            path = n.cost + float(cost[best_router.ID])
            if neigh_ID not in all_routers and neigh_ID not in visited:
                all_routers.append(neigh_ID)
            if neigh_ID not in cost:  #Meeting router for the first time
                cost[neigh_ID] = path
                previous[neigh_ID] = best_router.ID
            #if a lower cost route is found
            #We our cost and previous
            elif path < cost[neigh_ID]:
                cost[neigh_ID] = path
                previous[neigh_ID] = best_router.ID
    return (previous, cost)


#Maps the route from the original router to the target router
#Uses the 'previous' dictionary from djikstras algo to do this
def getItinerary(first_router, target_router, previous):
    itinerary = str(target_router)
    current_router = target_router
    try:
        while previous[current_router] != first_router:
            itinerary = previous[current_router] + itinerary
            current_router = previous[current_router]
        itinerary = first_router + itinerary
    except:
        pass
    return itinerary

#Resetting the heartbeat
'''
def defribilate(pulse):
    for router in pulse:
        pulse[router] = False
    return pulse
'''
#Checking whether nodes are dead or alive
#Will remove from known_routers if no response within a certain time
def checkPulse():

    global pulse
    local_pulse = pulse
    global known_routers
    local_KR = known_routers
    router_graveyard = []

    #Pulse will be updated every 3 seconds. If a packet isn't received within that time
    #then it's pronounced dead
    for living in local_pulse:
        if local_pulse[living] is False:
            router_graveyard.append(living) #Not living anymore lol

    for router in local_KR:
        if router.ID in router_graveyard:
            del local_pulse[router.ID]
            local_KR.remove(router)
    #Now we we update our global routers with the local routers
    known_routers = local_KR
    #Resetting the pulse
    for router in local_pulse:
        pulse[router] = False
    #pulse = defribilate(local_pulse)

    t2 = threading.Timer(3, checkPulse, [])
    t2.daemon = True
    t2.start()
    #Thread pulse to run every 3 seconds

def Output(OG_router):
    while True:
        previous, cost = dijkstra(OG_router, known_routers)
        #if len(known_routers) > 1:

        if pulse != {}:
            print "I am Router " + initial_router.ID
        for router in known_routers:
            if router.ID is not OG_router.ID and router.ID in pulse:
                route = getItinerary(OG_router.ID, router.ID, previous)
                print "Least cost path to router %s:%s and the cost is %s" %(router.ID, route, cost[router.ID])
        time.sleep(30)


########################__MAIN__PROGRAM__#######################################
input_file = sys.argv[1]
file = open(input_file, 'r')

file = file.read()

initial_router, all_routers = sort_input_file(file)
known_routers = list() #All routers including the initial one
known_routers.append(initial_router)
received = list()
pulse = dict() #Heartbeat

#print initial_router

#Setting up and binding UDP socket
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socket.bind(("localhost", int(initial_router.port)))



t1 = Thread(target = broadcast, kwargs = {'router': initial_router})
t1.daemon = True
t1.start()

checkPulse() #I wrote the thread for checkpulse into the function itself

t3 = Thread(target = Output, kwargs = {'OG_router': initial_router})
t3.daemon = True
t3.start()

while True:
    #Receiving packet
    try:
        received_packet, address = socket.recvfrom(1024)
        received_router, recv_neighs = sort_input_file(received_packet)
        #We won't rebroadcast to received_router
        recv_neighs.add(received_router.ID)

        if received_router.ID in pulse:
            if received_router.port != address[1]:
                for known in known_routers:
                    if known.port == address[1]:
                        for targets in known.neighs:
                            recv_neighs.add(targets.target_router.ID)

        known = False
        #print recv_neighs
        #print received_router.ID
        for KR in known_routers:
            #print KR.ID
            if received_router.ID is KR.ID:
                pulse[received_router.ID] = True
                known = True
                break
        if known is False:
            pulse[received_router.ID] = False
            known_routers.append(received_router)
            #Resetting pulse
            for key in pulse:
                pulse[key] = False

        #print pulse

        #rebroadcasting packet3

        for neighbour in initial_router.neighs:
            if neighbour.target_router.port != address[1]: #Makes sure to not send back to sender
                if neighbour.target_router.ID not in recv_neighs: #Doesn't send packet to shared neighbours
                    socket.sendto(received_packet, ("localhost", neighbour.target_router.port))

            # and received_router.ID not in received
        received.append(received_router.ID)
    except KeyboardInterrupt:
        print '\nKilled Router ' + initial_router.ID
        sys.exit()
