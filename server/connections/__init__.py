"""
define User:
    def socket_starts(self,socket) #gets called when the connection is ready; socket is the active connection
    def socket_process(self,identifier,content) #gets called for each message received
    def socket_updates(self) #gets called every 1./30 of a second if socket.updating == True
    def socket_closes(self) #gets called on loss of connection

    #note: socket_send(self,identifier,container) gets assigned before socket_starts
User can access socket by:
    self.socket_send(identifier,content = None) #to send messages
    self.socket_send() #to close socket

run_websocket_application_forever(User,path = r"/websocket",port = 8888)
    #accepts connections going to path,port
        #when a connection is opened a new User is created
"""

import sys
sys.path.append("tornado-3.1/")
import tornado.ioloop, tornado.web, tornado.websocket

import json
from queue import Queue,Empty
import threading
import time
import traceback

class MessageFormatError(Exception):
    pass

class MessageProcessingError(Exception):
    pass
    


class WebSocket(tornado.websocket.WebSocketHandler):
    active_sockets = set()
    User = None
    send_sleep_time = 1/30 #assumes all calculations in update are instant
    read_sleep_time = 1/1000
    assert (read_sleep_time < send_sleep_time) and (send_sleep_time % read_sleep_time < 1/1000), "read_sleep_time must be an aproximate fraction of send_sleep_time"

    def open(self):
        self.set_nodelay(True)
        self.active_sockets.add(self)

        self.send_queue = Queue()
        self.receive_queue = Queue()
        
        self.running = True
        self.updating = False

        self.user = None #to be initialized in the thread

        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def on_message(self, messages):
        self.receive_queue.put_nowait(messages)

    def load_messages(self):
        while True:
            try:
                messages = self.receive_queue.get_nowait()
            except Empty:
                break #break out of the while True

            try:
                messages = json.loads(messages)
            except Exception as e:
                raise MessageFormatError(e)
            
            if type(messages) is not list:
                raise MessageFormatError()

            for m in messages:
                if (type(m) is not list) or not(1 <= len(m) <= 2):
                    raise MessageFormatError()

                if type(m[0]) is not str:
                    raise MessageFormatError()

                try:
                    if len(m) == 2:
                        self.user.socket_process(m[0],m[1])
                    else:
                        self.user.socket_process(m[0],None)
                except Exception as e:
                    raise MessageProcessingError(e)


    def dump_messages(self):
        messages = []
        
        while True:
            try:
                messages.append(self.send_queue.get_nowait())
            except Empty:
                break #break out of the while True

        if len(messages):
            self.write_message(json.dumps(messages))

    def run(self):
        try:
            self.user = self.User()
            self.user.socket_send = self.send
            self.user.socket_starts()

            while self.running:

                self.user.socket_updates()
                self.dump_messages()
                now = time.time()
                while time.time()-now < self.send_sleep_time: #i want to read more often then dumping messages
                    self.load_messages()
                    time.sleep(self.send_sleep_time)

        except:
            traceback.print_last()
        finally:
            try:
                self.user.socket_closes()
            except:
                traceback.print_last()
            try:
                self.close()
            except:
                pass #i tryed, this is tornado's fault if it doesn't close

    def on_close(self):
        self.running = False
        self.active_sockets.remove(self)

    #def close(self): inherited
   
    def __call__(self,identifier = None,content = None):
        if identifier is None:
            self.close()
        else:
            assert isinstance(identifier,str), "identifier must be a string."
            if content is not None:
                self.send_queue.put_nowait([identifier,content])
            else:
                self.send_queue.put_nowait([identifier])

    send = __call__





def run_websocket_application_forever(User,path = r"/websocket",port = 8888):
    #User class checks
    assert callable(getattr(User, "socket_process", None)), "class has not defined socket_process(self,indentifier,content)."
    assert callable(getattr(User, "socket_updates", None)), "class has not defined socket_updates(self)."
    assert callable(getattr(User, "socket_starts", None)), "class has not defined socket_starts(self)."
    assert callable(getattr(User, "socket_closes", None)), "class has not defined socket_closes(self)."
    WebSocket.User = User
    

    application = tornado.web.Application([
        (path, WebSocket),
    ])

    application.listen(port)
    print("WebSocket application forever loop.")
    tornado.ioloop.IOLoop.instance().start()

