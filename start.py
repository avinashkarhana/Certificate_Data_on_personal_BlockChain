import subprocess

process1 = subprocess.Popen(["python3", "blockchainfileserver.py"])
print("File Server Started\n\n")
process2 = subprocess.Popen(["python3", "blockchainserver.py"])
print("Chain Server Started\n\n")
process3 = subprocess.Popen(["python3", "CertificatesonBlockChainMain.py"])
print("Client Started\n\n")
process1.wait()
process2.wait()
process3.wait()