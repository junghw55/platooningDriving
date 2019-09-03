import socket
import time
from threading import Thread
 
HOST = '192.168.0.6'
PORT = 55555
leader_IP=''
ipport=''
leader=''
close=''
 
def rcvMessage(sock):
   while True:
      try:
         data = sock.recv(1024)
         if not data:
            break
         test = data.decode()
         idzz = test[0:3]
   
         if idzz == 'por':
            global ipport
            ipport = test[4:len(test)]
            
            
         if idzz == 'lea':
            global leader
            leader = test[4:len(test)]
           

         if idzz == 'ipz':
            global leader_IP
            leader_IP = test[4:len(test)]

         if idzz == 'alr':
            global close
            close = test[4:len(test)]


#         print(data.decode())


      except:
         pass

def startConnect():
      print("startConnect!!!")
      sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sock.connect((HOST, PORT))
      t = Thread(target=rcvMessage, args=(sock,))
      t.daemon = True
      t.start()
      global close

      while True:
         if close == '0':
            msg = '/quit'
            time.sleep(0.001)
            if msg == '/quit':
               print("here")
               sock.send(msg.encode())
               break

      return int(leader), leader_IP, ipport
#startConnect()

