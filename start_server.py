import socketserver
import threading
import random
import time

HOST = ''
PORT = 55555
lock = threading.Lock() 
UserCount=0
goonzip=0
leader = 1
leader_IP=''
IP_port = random.randint(1,65535)
class UserManager: 

   def __init__(self):
      self.users = {} 

      
 
   def addUser(self, username, conn, addr): 
    

      lock.acquire() 
      self.users[username] = (conn, addr)
      lock.release() 

      self.sendMessageToAll('[%s] is in a server.' %username)
      print('+++  Number of Member [%d]' %len(self.users))
         
      return username
 
   def removeUser(self, username): 
      if username not in self.users:
         return
 
      lock.acquire()
      del self.users[username]
      lock.release()
 
      self.sendMessageToAll('[%s] get out.' %username)
      print('--- Number of Member [%d]' %len(self.users))
 
   def messageHandler(self, username, msg):
      if msg[0] != '/':
         self.sendMessageToAll('[%s] %s' %(username, msg))
         return
 
      if msg.strip() == '/quit': 
         self.removeUser(username)
         return -1

 
   def sendMessageToAll(self, msg):
      for conn, addr in self.users.values():
         conn.send(msg.encode())
           

class MyTcpHandler(socketserver.BaseRequestHandler):
   userman = UserManager()
   global UserCount

     
   def handle(self): # 
      global goonzip
      global leader
      global leader_IP
      global IP_port
      print('[%s] is connected' %self.client_address[0])
      print(len(self.userman.users))
     
      
      try:
         
         if leader == 1:
            leader_IP=self.client_address[0]
         
         username = self.registerUsername()
         self.userman.sendMessageToAll('por %d ' %IP_port)
         time.sleep(0.1)
         self.userman.sendMessageToAll('lea %d ' %leader)
         time.sleep(0.1)
         self.userman.sendMessageToAll('ipz '+leader_IP)
         time.sleep(0.1)
         self.userman.sendMessageToAll('alr 0')
         leader = 0
         
         msg = self.request.recv(1024)
         while msg:
            print(msg.decode())
            if self.userman.messageHandler(username, msg.decode()) == -1:
               self.request.close()
               break
            msg = self.request.recv(1024)
                 
      except Exception as e:
         print(e)
 
      print('[%s] is disconnected' %self.client_address[0])
      self.userman.removeUser(username)
 
   def registerUsername(self):
      if self.userman.addUser(self.client_address[0], self.request, self.client_address):
         return self.client_address[0]
 
class ChatingServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass
         
def runServer():
   print('+++ start server.')
  
 
   try:
      server = ChatingServer((HOST, PORT), MyTcpHandler)
      server.serve_forever()
   except KeyboardInterrupt:
      print('--- end server.')
      server.shutdown()
      server.server_close()
 
runServer()

