import socket
import matplotlib.pyplot as plt
from collections import deque

HOST = "0.0.0.0"
PORT = 5000
MAX_POINTS = 300

while True:  
    print(f"Listening on {HOST}:{PORT}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)

    print("Waiting for connection...")
    conn, addr = sock.accept()
    print("Connected by", addr)
    conn.setblocking(False)

    
    timestamps = deque(maxlen=MAX_POINTS)
    temps1 = deque(maxlen=MAX_POINTS)
    temps2 = deque(maxlen=MAX_POINTS)

    
    plt.close('all')
    plt.ion()
    fig, ax = plt.subplots()
    line1, = ax.plot([], [], label="Raw sensor")
    line2, = ax.plot([], [], label="Probe sensor")
    ax.set_xlabel("Time")
    ax.set_ylabel("Temperature (°C)")
    ax.legend()
    ax.grid(True)

    try:
        while True: 
            try:
                data = conn.recv(1024)
                if not data:
                    raise ConnectionResetError
                text = data.decode().strip()
                try:
                    ts, t1, t2 = text.split(",")
                except:
                    continue
                
                timestamps.append(float(ts))
                temps1.append(float(t1))
                temps2.append(float(t2))

                line1.set_data(timestamps, temps1)
                line2.set_data(timestamps, temps2)
                if timestamps:
                    ax.set_xlim(min(timestamps), max(timestamps))
                    ax.set_ylim(min(min(temps1, default=0), min(temps2, default=0)) - 3,
                                max(max(temps1, default=0), max(temps2, default=0)) + 3)
                plt.draw()
                plt.pause(0.01)

            except BlockingIOError:
                pass
            except (ConnectionResetError, OSError):
                print("Connection lost, waiting for reconnect...")
                break 
    finally:
        conn.close()
        sock.close()
        plt.close(fig)