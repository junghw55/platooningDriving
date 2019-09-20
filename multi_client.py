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
         msg_data = data.decode()
         if not data:
            break
         elif (msg_data[msg_data.rfind("]") + 2:] == 'forward'):
            both.turn(-100, 100, False)
         elif msg_data[msg_data.rfind("]") + 2:] == 'left':
            wheel.turn(60,20,False)
         elif msg_data[msg_data.rfind("]") + 2:] == 'backward':
            both.turn(100, 100, False)
         elif msg_data[msg_data.rfind("]") + 2:] == 'right':
            wheel.turn(-60,20,False)
         elif msg_data[msg_data.rfind("]") + 2:] == 'brake':
            both.brake()
         elif "new connect" in msg_data:
            sock.close()
            host = msg_data[msg_data.find("_")+1:msg_data.rfind("/")]
            port = msg_data[msg_data.rfind("/")+1:]
            print(host)
            print(port)
            time.sleep(5)
            runChat(str(host), int(port))

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
      if (keyboard.is_pressed('s')):  # s 는 split 을 뜻함.
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
