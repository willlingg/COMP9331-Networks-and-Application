import socket
import select
import datetime
import time

UDP_IP = "127.0.0.1"
UDP_PORT = 1099
MESSAGE = "PING"
CRLF = "\r\n"

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

#sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
RTT_list = []

for i in range(10):
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.settimeout(1.0)
    TIME = datetime.datetime.now().time()
    start = time.time()
    sock.sendto(('PING ' + str(i) + ' ' + str(TIME) + CRLF), (UDP_IP, UDP_PORT))
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        END =  time.time()
        RTT = int((END - start)*1000)
        RTT_list.append(RTT)
        print "Ping to " + UDP_IP + ' ' + "seq = " + str(i) + ', ' + 'rtt = ' + str(RTT) + 'ms'
    except:
        print "Ping to " + UDP_IP + ' ' + "seq = " + str(i) + ', ' + 'timed out'

length = len(RTT_list)
avg = sum(RTT_list)/length
print 'The Minimum rtt of received packets is ' + str(min(RTT_list)) + 'ms'
print 'The Maximum rtt of received packets is ' + str(max(RTT_list)) + 'ms'
print 'The Average rtt of received packets is ' + str(avg) + 'ms'
