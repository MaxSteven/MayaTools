# run: python -i <this file>
import Deadline.DeadlineConnect as Connect
import socket
import urllib2
deadlineIP = str(socket.gethostbyname(socket.gethostname()))
c = Connect.DeadlineCon(deadlineIP, 8082)
