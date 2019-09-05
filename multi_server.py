import SocketServer
import threading
from threading import Thread
import time
import keyboard
import nxt.locator
from nxt.sensor import *
from nxt.motor import *
from collections import OrderedDict

from multiprocessing import Process
#brick = nxt.locator.find_one_brick()
#wheel = nxt.Motor(brick, PORT_A)
#left = nxt.Motor(brick, PORT_B)
#right = nxt.Motor(brick, PORT_C)
#both = nxt.SynchronizedMotors(left, right, 0)
#leftboth = nxt.SynchronizedMotors(left, right, 100)
#rightboth = nxt.SynchronizedMotors(right, left, 100)

brick = None
wheel= None
left = None
right = None
both = None

HOST = ''
PORT = None
lock = threading.Lock()

class CarManager:

   def __init__(self):
      self.cars = OrderedDict()

   def addCar(self, car_ip, conn, addr):
      if car_ip in self.cars:
         conn.send('duplicate.\n'.encode())
         return None

      lock.acquire()
      self.cars[car_ip] = (conn, addr)
      lock.release()

      self.sendMessageToAll('[%s] car is connect.' %car_ip)
      print('+++ current car num [%d]' %len(self.cars))
      print(self.cars[car_ip])
      return car_ip

   def removeCar(self, car_ip, new_port):
      if car_ip not in self.cars:
         return

      for idc, c in enumerate(self.cars.keys(),0):
         if car_ip == c:
            location = idc
            break
      print("location index")
      print(location)
      #else:
      #   print("asdfasdfasdfasdf")
      #   print(self.cars)
      #   location = self.cars.index(car_ip)
      lock.acquire()

      del self.cars[c]

      for idc , c in enumerate(self.cars.keys(),0):
         if idc >= location:
            print(c)
            self.sendMessageTo(c, "new connect_" + car_ip + "/" + new_port)
            del self.cars[c]
      lock.release()

      self.sendMessageToAll('[%s] car byebye' %car_ip)
      print('--- current car num [%d]' %len(self.cars))
      return self.cars, location

   def messageHandler(self, car_ip, msg):
      if msg[0] != '/':
         self.sendMessageToAll('[%s] %s' %(car_ip, msg))
         return

      if msg.strip() == '/quit':
         self.removeCar(car_ip)
         return -1

   def sendMessageToAll(self, msg):
      for conn, addr in self.cars.values():
         #print(addr)
         if '192.168.25.6' not in addr:
            print("----------------")
            print("send message")
            print(addr)
            conn.sendto(msg.encode(), addr)
         # conn.send(msg.encode())

      # conn.sendto(msg.encode(), ('192.168.25.9', 54354))

   def sendMessageToNew(self, car_location, msg):
      count = 0
      for conn, addr in self.cars.values():
         count = count + 1
         if count > car_location:
            conn.sendto(msg.encode(), addr)
   
   def sendMessageTo(self, car_ip, msg):
      for conn,addr in self.cars.values():
         if car_ip in addr:
            print("sendsend")
            print(car_ip)
            print(msg)
            conn.sendto(msg.encode(), addr)
            break

   def keyboard_handle(self):
      global brick
      global wheel
      global left
      global right
      global both


      processes = Thread(target=self.messageHandler, args=('leader','w',))
      while True:
            flag = 0
            #if(keyboard.is_pressed('q')):
            #   flag = 5
            #   processes = Thread(target=self.messageHandler, args=('leader','q',))
            if (keyboard.is_pressed('w')):
               flag = 1
               processes = Thread(target=self.messageHandler, args=('leader','w',))
            elif(keyboard.is_pressed('a')):
               flag = 2
               processes = Thread(target=self.messageHandler, args=('leader','a',))
            elif(keyboard.is_pressed('s')):
               flag = 3
               processes = Thread(target=self.messageHandler, args=('leader','s',))
            elif(keyboard.is_pressed('d')):
               flag = 4
               processes = Thread(target=self.messageHandler, args=('leader','d',))

            #if flag == 5:
            #   processes.start()
            #   both.brake()
            if flag == 1:
               processes.start()
               both.turn(-100, 500, False)
            elif flag == 2:
               processes.start()
               wheel.turn(60,20,False)
            elif flag == 3:
               processes.start()
               both.turn(100, 100, False)
            elif flag == 4:
               processes.start()
               wheel.turn(-60,20,False)

   def keyboard_brake(self):
      global brick
      global wheel
      global left
      global right
      global both


      processes = Thread(target=self.messageHandler, args=('leader','w',))
      while True:
            flag = 0
            if (keyboard.is_pressed('q')):
               flag = 6
               processes = Thread(target=self.messageHandler, args=('leader','q',))

            if flag == 6:
               processes.start()
               both.brake()


class MyTcpHandler(SocketServer.BaseRequestHandler):
   print("handle comein")
   car_class = CarManager()

   t = Thread(target=car_class.keyboard_handle)
   t.daemon = True
   t.start()

   b = Thread(target=car_class.keyboard_brake)
   b.daemon = True
   b.start()
   def handle(self):
      print('[%s] connect' %self.client_address[0])
      print('[%s] connect' %self.client_address[1])
      msg_buffer = ''
      try:
         car_ip = self.registercar_ip()


         msg = self.request.recv(1024)
         while msg:
            print(msg.decode())
            msg_buffer = msg.decode()
            if "stop" in msg_buffer:
               self.request.close()
               break
            msg = self.request.recv(1024)


      except Exception as e:
         print(e)

      new_port = msg_buffer[msg_buffer.find("_")+1:]
      print('[%s] connect stop' %self.client_address[0])
      print(self.client_address[0])
      print(new_port)
      print("-----=-=-=-=-=-=-=-=-=-=-=-=-")
      car_list, car_location = self.car_class.removeCar(self.client_address[0], new_port)


      #if car_location != 0:
      #for car in car_list:
      #   self.car_class.sendMessageToNew(car_location, "new connect_" + self.client_address[0] + "/" + new_port)

   def registercar_ip(self):
      while True:
         # self.request.send('login ID:'.encode())
         # car_ip = self.request.recv(1024)
         # car_ip = car_ip.decode().strip()
         if self.car_class.addCar(self.client_address[0], self.request, self.client_address):
            return self.client_address[0]

class ChatingServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def runServer(bricks, wheels, lefts, rights, boths, port):
   global brick
   global wheel
   global left
   global right
   global both
   global PORT

   brick = bricks
   wheel = wheels
   left = lefts
   right = rights
   both = boths
   PORT = port
   print('+++ leader server start')
   print('+++ stop :  Ctrl-C')


   try:
      server = ChatingServer((HOST, PORT), MyTcpHandler)
      server.serve_forever()
   except KeyboardInterrupt:
      print('--- leader server quit')
      server.shutdown()
      server.server_close()

#runServer()
