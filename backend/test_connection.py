import socket
import time

import numpy as np

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    # Connect to server and send data
    sock.connect(('14.137.209.102', 7777))
    sock.sendall(b'\0')

    while True:
        data = sock.recv(2048)
        print(np.frombuffer(data))
        time.sleep(0.5)
