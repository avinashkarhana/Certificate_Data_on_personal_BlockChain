import hashlib
import os
import socket                                         
import urllib.request as urllib2
import time
import datetime
import re
import subprocess

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

def sconnect(host,port,m):
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((host,port))
        s.send(m.encode())
        msg = s.recv(1024)   
        if m !="checksum":
            return (msg.decode('ascii'))
        else:
            return (msg)
        s.close()
    except:
        print("Node not active!")
        
#inital connection to Chain        
                           
myport = 9999
fileoq=open("chain.txt","r")
rdblq=fileoq.readable()
fileoq.close()
if not rdblq:
    fileo=open("chain.txt","w")  
    fileo.write("blockno:0;prevblockhash:0;data:genesis-block;timestamp:2019-05-27 01:53:59;blockhash:00cfb0ebf5ebe7eac75659241702a3a4967cf415ec63ef55a1487ac6")
    fileo.close()
    fileo=open("nodes.txt","w")  
    fileo.write("127.0.0.1")
    fileo.close()
    checkchain(-1,"check") 
    x=sconnect('127.0.0.1',myport,"first")
    print(x)
else:
    x=sconnect('127.0.0.1',myport,"con")
    print(x)
    
def checkchain(bl,ze):
    d={}
    fileo=open("nodes.txt","r")
    rdbl=fileo.readable()
    if rdbl:
        for l in fileo.readlines():
            msg=sconnect(l,9999,"checksum")
            if d.get(msg)== None:
                    d[msg]=[]
                    d[msg].append(1)
                    d[msg].append(l)
            else:
                    [d[msg]][0]=[d[msg]][0]+1
    x=0
    lr=0
    al=""
    for a in d:
        if d[a][0]>=lr :
            al=a
            lr=d[a][0]
        x=x+d[a][0]
    x=x/2
    tr=filehash("chain.txt")
    if d[tr][0]>x or d[tr][0]==d[al][0]:
        if ze=="add":
            xcv=addblock(bl)
        if ze=="check":
            xcv=findcert(bl)
    else:
         print("Updating Chain !")
         url = "http://"+d[al][1]+":8000/chain.txt"
         downchain(url)
         if ze=="add":
            xcv=addblock(bl)
         if ze=="check":
            xcv=findcert(bl)
    return(xcv)
            
    
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


class block: 
    blockno=0
    blockhash=""
    prevblockhash=""
    data=""
    timestamp=""
    x=""
    
    def __init__(self,blkno,prevh,bdata):
        self.blockno=blkno
        self.prevblockhash=prevh
        self.data=bdata
        self.ts = time.time() 
        self.timestamp=datetime.datetime.fromtimestamp(self.ts).strftime('%Y-%m-%d_%H:%M:%S')
        self.x="blockno:"+str(blkno)+";prevblockhash:"+str(prevh)+";data:"+str(bdata)+";timestamp:"+str(self.timestamp)
        self.blockhash=hashlib.sha224(str.encode(self.x)).hexdigest()

def createblock(ndata):
    lb=red("chain.txt")
    xx=lb.split(";")
    zz={}
    for a in xx:
        zz[a.split(":")[0]]=a.split(":")[1]
    blkno=int(zz["blockno"])+1
    prevh=zz["blockhash"]
    b=block(blkno,prevh,ndata)
    return(b)

def addblock(bl):
    li="\nblockno:"+str(bl.blockno)+";prevblockhash:"+str(bl.prevblockhash)+";data:"+str(bl.data)+";timestamp:"+str(bl.timestamp)+";blockhash:"+str(bl.blockhash)
    fileo=open("chain.txt","a")
    fileo.write(li)
    fileo.close()
    #all nodes command to add block
    fileo=open("nodes.txt","r")
    rdbl=fileo.readable()
    if rdbl:
        for l in fileo.readlines():
            msg=sconnect(l,9999,"AddBlock@"+li)
    
    print("Certificate Added")

def findcert(bl):
        fileo=open("chain.txt","r")
        rdbl=fileo.readable()
        if rdbl:   
            for l in fileo.readlines():
                if l.split(";")[0].split(":")[1]!="0":
                    y=l.split(";")[2].split("&")[0].split(">")[1]
                    if int(y)==int(bl):
                        xcv=l.split(";")[2].split(":")[1].split("&")
                        return(xcv)
            else:return("Certificate Not Found!")
        fileo.close()
    
#Main panel Functions
def addcert():
    r=""
    s="000000000"
    n="1"
    cnt=0
    print("\n\n# Enter the data of Certificate #\n")
    print("Certificate Number: ")
    cn=input()
    def namechk(word):
         if re.match("^[a-zA-Z ]*$", word):return(True)
         else: return(False)
    while not namechk(n):
        if cnt>0:
            print("You enetred something Wrong in Name (Name can only br Alphabets of upper and lowercase)")
        print("Name: ")
        n=input()
        cnt=cnt+1
    cnt=0
    print("\nCourse: ")
    c=input()
    while r!="PASS" and r!="FAIL":
        if cnt>0:
            print("You enetred something other than PASS or FAIL")
        print("\nResult(PASS/FAIL): ")
        r=input()
        cnt=cnt+1
    cnt=0
    while s[4]!="-" or int(s[0:4])>int(s[5:]) or len(s)!=9:    
        if cnt>0:
            print("You enetred something Wrong in Session Ex. 1978-1983(a-b, where a<b)")
        print("\nSession: ")
        s=input()
        if len(s)<7:s="0000000"
        cnt=cnt+1
    cnt=0
    dt="Certificate Number>"+str(cn)+"&Name>"+n+"&Course>"+c+"&Session>"+s+"&Result>"+r
    print(dt)
    rb=createblock(dt)
    checkchain(rb,"add")
    
def viewcert():
    print("\n\n# Enter of Certificate Number: #\n")
    print("Certificate Number: ")
    n=input()
    rb=n
    z=checkchain(rb,"check")   
    print("\n",z)
    
#Main Usage pannel for Admin;
g=True
while g:
    print("\n######################################################\nChoose from options\n1.Add a certificate\n2.View Certificate\n* To Exit\n____________________________________\nEnter the choice: ")
    opt=input()
    if opt=="*":
        print("Exiting !\n\n")
        break
    opt=int(opt)
    if opt==1:
        addcert()
    elif opt==2:
        viewcert()
    else:
        print("Invalid Option !")

    