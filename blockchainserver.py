import socket
import hashlib
import urllib.request as urllib2

def red(file):
    with open(file, 'r') as f:
        lines = f.read().splitlines()
        last_line = lines[-1]
        return(last_line)
    
def downchain(url):
    file_name = url.split('/')[-1]
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(u.getheader('Content-Length'))
    print ("Downloading: %s Bytes: %s" % (file_name, file_size))
    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print (status),
    f.close()
    
def filehash(x):
    if type(x) is list:
        filelst=x
    if type(x) is str:
        fnamelst=[x]
    else:return("Invalid file name or list of file names !")
    def hash_bytestr_iter(bytesiter, hasher, ashexstr=False):
        for block in bytesiter:
            hasher.update(block)
        if ashexstr:  
            return hasher.hexdigest()
        else: 
            return(hasher.digest())
        

    def file_as_blockiter(afile, blocksize=65536):
        with afile:
            block = afile.read(blocksize)
            while len(block) > 0:
                yield block
                block = afile.read(blocksize)
    d=[]
    for fname in fnamelst:
        if len(fnamelst)==1:
            return(hash_bytestr_iter(file_as_blockiter(open(fname, 'rb')), hashlib.sha256()))
        else:
            d.append(hash_bytestr_iter(file_as_blockiter(open(fname, 'rb')), hashlib.sha256()))
        return(d)
    
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
port = 9999
serversocket.bind(('', port))                                  
serversocket.listen(100)                                           
print("#SERVER STARTED#")
while True:
   clientsocket,addr = serversocket.accept() 
   data = clientsocket.recv(1024)
   data = data.decode('ascii')
   msg = 'Client side Joined the chain network !'+ "\r\n"
   if data=="first":
        ip="127.0.0.1"#change ip as per root and first node
        print("Updating Nodes From : ",ip)
        url = "http://"+ip+":8000/nodes.txt" 
        downchain(url)
        cb=red("nodes.txt")
        if cb!=str(addr[0]):
            fileo=open("nodes.txt","a")
            fileo.write(str(addr[0]))
            fileo.close()
        print("New Node connected from %s" % str(addr))
        clientsocket.send(msg.encode())
   if data=="con":
        clientsocket.send(msg.encode())
   if data=="checksum":
        chksm=filehash("chain.txt")
        clientsocket.send(chksm)
   if data[0:8]=="AddBlock":
        data=data.split("@")[1]
        zo=red("chain.txt")
        zo=int(zo.split(";")[0].split(":")[1])
        zx=int(data.split(";")[0].split(":")[1])
        if zo==zx-1:
            fileo=open("chain.txt","a")
            fileo.write(data)
            fileo.close()
            clientsocket.send(b'')
        elif zo==zx:clientsocket.send(b'')
        else:
            print("Updating Chain From : ",addr[0])
            url = "http://"+str(addr[0])+":8000/chain.txt"
            downchain(url)
            clientsocket.send(b'')
   clientsocket.close()