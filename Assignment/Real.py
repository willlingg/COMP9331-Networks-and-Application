import sys
import time
import threading
from threading import Thread
import os
from collections import deque
from collections import defaultdict
from socket import *

class Edge:
    def __init__(self, dest, cost):
        self.dest = dest
        self.cost = cost

class Node:
    def __init__(self, id, port):
        self.id = id
        self.port = port
        self.edges = []
    '''
    def __eq__(self, other):
        if self.id == other.id:
            return True
        else:
            return False
    '''
    def addEdge(self, dest, cost):
        e = Edge(dest, cost)
        self.edges.append(e)

#processess data according to the config.txt format and returns a node object
#and a list of the destinations the node can reach
#argument is a string in the format described in report
def processLinks(data):
    lines = data.split("\n")
    originNode = Node(lines[1], lines[0])
    n = int(lines[2])
    destinations = set()
    for i in range(3,n+3):
        info = lines[i].split(" ")
        destinations.add(info[0])
        newNode = Node(info[0], int(info[2]))
        originNode.addEdge(newNode, float(info[1]))
    return (originNode, destinations)

#creates and broadcasts the packet information for this router
#input is the homeNode
def makeBroadcast(originNode):
    #global broadcasted
    #broadcasted = []
    while True:
        data = str(originNode.port) + "\n"
        data += originNode.id + "\n"
        data += str(len(originNode.edges)) + "\n"
        for edge in originNode.edges:
            data += edge.dest.id+" "+str(edge.cost)+" "+str(edge.dest.port)+"\n"
        data = data[:-1]
        for n in originNode.edges:
            sendPacket(n.dest.port, data)
        time.sleep(1)
    '''
    t1 = threading.Timer(1, makeBroadcast, [homeNode])
    t1.daemon = True
    t1.start()
    '''

#forwards a packet to a specifed port on local computer
#arguments are the port number and the data to be sent
def sendPacket(port, data):
    hostSocket.sendto(data, ('127.0.0.1', port))

#implementation of djikstras algorithm
#arguments are the homeNode and a list of active nodes
#returns a tuple containing 2 hashmaps. First mapps node id to the id of their
#previously traveled node. The second maps node id to cost to reach node
def performSearch(originNode, nodes):
    routers = [originNode.id]
    visited = []
    cost = {originNode.id:0}
    previous = {originNode.id:originNode.id}
    while True:
        best_route = None
        for router in routers:
            if best_route is None or cost[router] < best_route:
                best_route = cost[router]
                current_router = router
        #We cycle through the routers. Works well if there aren't a tonne
        #otherwise it'll take too long
        if len(routers) == 0:
            break
        routers.remove(current_router)

        no_routers = 0
        for n in nodes: #get actual node data from nodes list
            if n.id == current_router:
                best_router = n
                break
            no_routers += 1
        if no_routers == len(nodes): #if destination isn't in active nodes
            continue


        visited.append(best_router.id)
        for n in best_router.edges:
            neigh_ID = n.dest.id
            path = n.cost + float(cost[best_router.id])
            if neigh_ID not in routers and neigh_ID not in visited:
                routers.append(neigh_ID)
            if neigh_ID not in cost:  #Meeting router for the first time
                cost[neigh_ID] = path
                previous[neigh_ID] = best_router.id
            elif path < cost[neigh_ID]: #if a lower cost path is found
                cost[neigh_ID] = path
                previous[neigh_ID] = best_router.id

    return (previous, cost)

#finds the path from the home node to a destination using previous dicitonary
#arguments are start id, destination id, dictionary of prev dest from
#performSearch function
def getPath(start, dest, previous):
    path = str(dest)
    curr = dest
    while previous[curr] != start:
        path = previous[curr] + path
        curr = previous[curr]
    path = start + path
    return path

#calls search algorithm and finds fastest path to each router and prints info
#takes the homeNode as an input
#also starts thread which runs every 30 seconds
def printSearch(originNode):
    #global nodes
    #graph = nodes
    while True:
        previous, distance = performSearch(originNode, nodes)
        print distance
        if len(nodes) > 1:
            print "I am Router " + originNode.id
        for n in distance:
            #print n.id
            if n is not originNode.id:
                path = getPath(originNode.id, n, previous)
                print "Least cost path to router %s:%s and the cost is %s" %(n, path, distance[n])
                #print "least-cost path to node "+str(n.id)+": "+str(path)+" and the cost is "+str(distance[n.id])
        time.sleep(5)
    '''
    t2 = threading.Timer(5, printSearch, [originNode])
    t2.daemon = True
    t2.start()
    '''
#check to see if any node has died
#if it hasn't received a packet from a node for 5 seconds it removes it
def checkHeartbeat():

    dead = []
    global heartbeat
    global nodes
    beats = heartbeat
    newNodes = nodes

    for node in beats:
        if beats[node] is False:
            dead.append(node)

    for n in newNodes:
        if n.id in dead:
            print "lost " + n.id
            del beats[n.id]
            newNodes.remove(n)
    nodes = newNodes
    #resetting heartbeat
    for key in beats:
        heartbeat[key] = False

    #heartbeat = resetHeartbeat(beats)
    t3 = threading.Timer(5, checkHeartbeat, [])
    t3.daemon = True
    t3.start()
    #t3 = threading.Timer(5, checkHeartbeat, [])



#resets all heartbeat mappings to 0
def resetHeartbeat(heartbeat):
    for key in heartbeat:
        heartbeat[key] = False
    return heartbeat

#################   MAIN PROGRAM START #####################################
homeId = sys.argv[1]
port = int(sys.argv[2])
startFile = sys.argv[3]

homeNode = Node(homeId, port)

#get neighbours from txt file and create home node
f = open(startFile, "r")
data = f.read()
data = str(port) + "\n" + homeId + "\n" + data
homeNode, destinations = processLinks(data)


#bind socket
hostSocket = socket(AF_INET, SOCK_DGRAM)
hostSocket.bind(('127.0.0.1', port))
hostSocket.settimeout(8)


nodes = [] #list of routers it has received from
nodes.append(homeNode)
broadcasted = [] #keeps track of id's of received packets, reset every sec
heartbeat = {} #will test for dead routers

t1 = Thread(target = makeBroadcast, kwargs = {'originNode': homeNode})
t2 = Thread(target = printSearch, kwargs = {'originNode': homeNode})
'''
t3 = Thread(target = checkHeartbeat, kwargs = {})
t3.daemon = True
t3.start()
'''
t1.daemon = True
t1.start()
t2.daemon = True
t2.start()

#makeBroadcast(homeNode) #start broadcasting thread
#printSearch(homeNode) #start searching thread
checkHeartbeat() #start heartbeat thread

previous, distance = performSearch(homeNode, nodes)
#print previous
#print distance
'''
for n in nodes:
    path = getPath(homeNode.id, n.id, previous)
    print "Least cost path to router %s:%s and the cost is %s" %(n.id, path, distance[n.id])
'''

while True:
    try:
        broadcast, sender = hostSocket.recvfrom(1024)
        newNode, destinations = processLinks(broadcast)
        destinations.add(newNode.id) #won't forward to these destinations


        #if this packet is a forwarded one, add senders edges to destinations
        if newNode.port != sender[1] and newNode.id in heartbeat:
            for n in nodes:
                if n.port == sender[1]:
                    for d in n.edges:
                        destinations.add(d.dest.id)

        #print destinations
        existing = False
        for n in nodes:
            if newNode.id is n.id:
                #try:
                heartbeat[newNode.id] = True
                #except KeyError:
                    #pass
                existing = True
                break
        if existing is False:
            #try:
            heartbeat[newNode.id] = 0
            #except KeyError:
            #    pass
            nodes.append(newNode)

            for key in heartbeat:
                heartbeat[key] = False
            #heartbeat = resetHeartbeat(heartbeat)
            #print str(len(nodes)) + " nodes"

        for n in homeNode.edges: #forward packets
            if n.dest.id not in destinations and n.dest.port != sender[1] and newNode.id not in broadcasted:
                sendPacket(n.dest.port, broadcast) #forward the packet
        broadcasted.append(newNode.id)
    except timeout:
        print "timeout"
