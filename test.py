import socket, json
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('192.168.1.7',3333))
s.send('{"id":0,"jsonrpc":"2.0","method":"miner_getstat1"}'.encode("utf-8"))
j=s.recv(2048)
s.close()
r=json.loads(j.decode("utf-8"))
print (r)
