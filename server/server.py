#! python3
import connections
import user

import threading
import time

def main():
    threading.Thread(target = lambda:connections.run_websocket_application_forever(user.User)).start() #fire and forget
    time.sleep(1)
    print("main thread continues")

if __name__ == "__main__":
    main()