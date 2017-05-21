import socket
import time
import functools

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 50007              # Arbitrary non-privileged port
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(5000)
s.bind((HOST, PORT))
s.listen(1)
conn, addr = s.accept()
conn.settimeout(5000)
print('Connected by', addr)
close = False
while not close:
    data = conn.recv(1024)
    if not data:
        print("Sleep")
        conn.send(bytes("ping", "ascii"))
        time.sleep(1)
    else:
        print("RAW: ", data)
        data = str(data.decode('ascii')).split('\\n')
        for line in data:
            try:
                if line == 'exit':
                    print("Exit")
                    close = True
                    break
                else:
                    print("RawElse: ", str(line).strip().split(' '))
                    x, y = filter(lambda a: a != '', str(line).strip().split(' '))
                    print(x, " ", y)
            except Exception:
                raise Exception(line)

        conn.send(bytes("ping", "ascii"))


conn.close()
