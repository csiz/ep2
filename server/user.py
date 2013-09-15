import time

class User:
    def __init__(self):
        self.updating = False
        self.socket_send = ...
        
    def socket_process(self,identifier,content):
        if identifier in self.valid_process:
            if content is not None:
                getattr(self,identifier)(content)
            else:
                getattr(self,identifier)()

    def socket_starts(self):
        print("User opened",id(self))
        self.socket_send("greet")

    def socket_updates(self):
        if self.updating:
            self.socket_send("time",time.time())

    def socket_closes(self):
        print("User closed",id(self))

    """
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    available messages to process follows:
    xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

    """

    valid_process = {"echo","ack","start","stop"}

    def echo(self,content):
        self.socket_send("message",content)

    def ack(self):
        pass

    def start(self):
        self.updating = True

    def stop(self):
        self.updating = False


    