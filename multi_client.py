import start_client
import multi_server
import keyboard
import socket
from threading import Thread
import time
import nxt.locator
from nxt.sensor import *
from nxt.motor import *
import random

brick = nxt.locator.find_one_brick()
wheel = nxt.Motor(brick, PORT_A)
left = nxt.Motor(brick, PORT_B)
right = nxt.Motor(brick, PORT_C)
both = nxt.SynchronizedMotors(left, right, 0)
#leftboth = nxt.SynchronizedMotors(left, right, 100)
#rightboth = nxt.SynchronizedMotors(right, left, 100)



def rcvMsg(sock):
   host = None
   port = None
   while True:
      try:
         data = sock.recv(1024)
         test = data.decode()
         if not data:
            break
         elif (test[test.rfind("]") + 2:] == 'w'):
            both.turn(-100, 100, False)
         elif test[test.rfind("]") + 2:] == 'a':
            wheel.turn(60,20,False)
         elif test[test.rfind("]") + 2:] == 's':
            both.turn(100, 100, False)
         elif test[test.rfind("]") + 2:] == 'd':
            wheel.turn(-60,20,False)
         elif "new connect" in test:
            sock.close()
            host = test[test.find("_")+1:test.rfind("/")]
            port = test[test.rfind("/")+1:]
            print(host)
            print(port)
            time.sleep(5)
            runChat(host, port)

         print(data.decode())
      except:
         pass

def runChat(HOST, PORT):
   print("runChat")
   print(HOST)
   print(PORT)
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   print("sock create ok")
   sock.connect((HOST, PORT))
   print("connect....")
   #except:
   #      print("retry")
   #      time.sleep(2)
   #      runChat()

   t = Thread(target=rcvMsg, args=(sock,))
   t.daemon = True
   t.start()

   while True:
      if (keyboard.is_pressed('m')):
         new_port = random.randint(1,65535)
         print("byebye")
         sock.send('stop_'+str(new_port).encode())
         sock.close()
         print("new port")
         print(new_port)
         multi_server.runServer(brick, wheel, left, right, both, new_port)
         break

leader, leader_IP, ipport = start_client.startConnect()

print(leader)
print(leader_IP)
print(ipport)

if int(leader) == 1:
   print("I'm leader")
   multi_server.runServer(brick, wheel, left, right, both, int(ipport))
else:
   print("I'm not leader")
   runChat(leader_IP, int(ipport))