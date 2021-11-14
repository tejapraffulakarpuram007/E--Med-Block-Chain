import ipfshttpclient
import requests

input("Welcome, Please ensure IPFS daemon is running. If not, Use command 'ipfs daemon'")

try:
	client = ipfshttpclient.connect('/ip4/192.168.56.101/tcp/5001/http')
	filename = input("Enter the filename stored in current directory (with extension)")
	res = client.add(filename)
	print("The hash of file is : ",res['Hash'])
	ofid = input("\nEnter the Officer ID")
	officer = "resource:org.jro.Officer#"+str(ofid)
	rojid = input("\nEnter the Research object ID")
	print("\n Adding the research object to the blockchain")
	r = requests.post('http://localhost:8080/api/Add', data = { "$class": "org.jro.Add","rojId": rojid, "node": res['Hash'], "creator": officer })
	if r.status_code==200:
		print("\n Success")
	

except ConnectionRefusedError:
	print("Connection error, Please ensure ipfs daemon is running.")
