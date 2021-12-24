import hashlib
import socket

def get_execution_id():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = 'time-a-g.nist.gov'
    port = 13
    s.connect((host, port))
    timestamp = ''
    while True:
        data = s.recv(1024)
        if data:
            timestamp = data.decode('utf-8')
        else: 
            break
    s.close()
    exe_id = hashlib.sha256(timestamp.encode('utf8')).hexdigest()
    return exe_id