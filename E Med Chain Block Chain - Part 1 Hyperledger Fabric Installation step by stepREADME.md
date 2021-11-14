#   Part 1 Hyperledger Fabric Installation step by step E Med Chain Block Chain 
 

Prerequisites

Quick start (using codebase)
Prerequisites
Nodejs 10 and 12 (10.19 and 12.16 tested)
PostgreSQL 9.5 or greater
jq
Linux-based operating system, such as Ubuntu or MacOS
golang (optional)
For e2e testing

--------------
Step 1 — Set up droplet

For new droplets, set the locale (choose en_US.UTF-8 if in doubt) and do apt update/upgrade.

$ sudo dpkg-reconfigure locales
$ sudo apt-get update && sudo apt-get upgrade

Step 2 — Set up new user  (use user who is not root)

There will be errors if you try to install Hyperledger Explorer as a root, therefore, for the rest of the set-up, you will be using the new user “tej” to do it. You will be prompted to set up a new password for the user which you will be using later. You will also need to give “tej” the sudo access by setting the permission. (chose any name).

$ sudo adduser tej 
$ sudo usermod -aG sudo tej

Switch user to "tej"
$ su - tej

Step 3 — Set up the prerequisites
 To run Fabric 2.2 and Explorer will just be using docker.
$ sudo apt-get install curl git docker.io docker-compose nodejs npm python

#Updating npm to 5.6.0

$ sudo npm install npm@5.6.0 -g

#Setting up docker configuration

$ sudo usermod -a -G docker $USER
$ sudo systemctl start docker
$ sudo systemctl enable docker

#Installing golang
$ wget https://dl.google.com/go/go1.13.6.linux-amd64.tar.gz
$ tar -xzvf go1.13.6.linux-amd64.tar.gz
$ sudo mv go/ /usr/local

#edit gopath in .bashrc
pico ~/.bashrc

#(add these 2 lines to end of .bashrc file)
export GOPATH=/usr/local/go
export PATH=$PATH:$GOPATH/bin

#exit and log back in as tej ---- very important 
exit
$ su - tej

Step 4 — Set up Hyperledger Fabric Test Network
After installing the dependencies, you can now set up Hyperledger Fabric 2.3.

$ curl -sSL https://bit.ly/2ysbOFE | bash -s 2.3.0
$ cd fabric-samples/test-network
$ ./network.sh up createChannel

This will bring up the Fabric Test Network creating a channel with it. Check using “docker ps -a” to see if it is up and running.

$ docker ps -a

Step 5 — Download files required to install Hyperledger Explorer


# Now create a new folder for Explorer 
$ cd ~/
$ mkdir explorer
$ cd explorer/

# Download the files you need to setup Explorer

$ wget https://raw.githubusercontent.com/hyperledger/blockchain-explorer/master/examples/net1/config.json
$ wget https://raw.githubusercontent.com/hyperledger/blockchain-explorer/master/examples/net1/connection-profile/test-network.json -P connection-profile
$ wget https://raw.githubusercontent.com/hyperledger/blockchain-explorer/master/docker-compose.yaml

Step 6 — Copy your Test Network crypto artifact directory to your explorer folder

cp -r ~/fabric-samples/test-network/organizations/   ~/explorer/

Step 7 — Edit the docker compose file to the right path

pico docker-compose.yaml

# Make sure the volumes section is as below: the volume section at the end of the file.

Edit network name and path to volumes to be mounted on Explorer container (docker-compose.yaml) to align with your environment.
--------------------------------------------------------
volumes:
- ./config.json:/opt/explorer/app/platform/fabric/config.json
- ./connection-profile:/opt/explorer/app/platform/fabric/connection-profile
- ./organizations:/tmp/crypto
- walletstore:/opt/wallet
---------------------------------------------------------------
When you connect Explorer to your fabric network through bridge network, you need to set DISCOVERY_AS_LOCALHOST to false for disabling hostname mapping into localhost.

To be set up as 
-----------------------------------------------------
services:

  ...

  explorer.mynetwork.com:

    ...

    environment:
      - DISCOVERY_AS_LOCALHOST=false

-----------------------------------------------------------------

if you prefer to change the default password, you can edit to any thing
and Edit path to admin certificate and secret (private) key in the connection profile (test-network.json). You need to specify with the absolute path on Explorer container.

$ pico connection-profile/test-network.json
----------------------------------------------------
  "organizations": {
    "Org1MSP": {
      "adminPrivateKey": {
        "path": "/tmp/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp/keystore/priv_sk"
      ...
      ...
      "signedCert": {
        "path": "/tmp/crypto/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp/signcerts/Admin@org1.example.com-cert.pem"
      }
--------------------------------------------------------

Step 8 — Start Hyperledger Explorer

You should be ready to start Explorer.

# To start Hyperledger Explorer

$ docker-compose up -d

 #  To Clean up and Stop 

To stop services without removing persistent data, run the following:

$ docker-compose down

# If you changed any config, clear it out with this and start again

$ docker-compose down -v

----- Integrating PostgreSQL---------

Comands to check the Fabric Network 
-------------------------------------
$ docker ps -a ---  to check 

if  Fabric network is shut down and to start use

 $ ./network.sh up createChannel 

where to shutdown use 

 $ ./network.sh down 
------------------------------------------

step 9 - Start Hyperledger Fabric network

Step -10 :Clone this repository to get the latest using the following command.

$ git clone https://github.com/hyperledger/blockchain-explorer.git

$ cd blockchain-explorer

Step -11 Database Setup

$ cd blockchain-explorer/app

# Modify app/explorerconfig.json to update PostgreSQL database settings.

$ pico app/explorerconfig.json

--------------------------------------------------
"postgreSQL": {
    "host": "127.0.0.1",
    "port": "5432",
    "database": "fabricexplorer",
    "username": "hppoc",
    "passwd": "password"
}
---------------------------------------------------

Step 12 - Important repeat after every git pull (in some case you may need to apply permission to db/ directory, from blockchain-explorer/app/persistence/fabric/postgreSQL run: 

$ chmod -R 775 db/

Step -13  Update configuration

#  Modify app/platform/fabric/config.json to define your fabric network connection profile:

 $ pico app/platform/fabric/config.json
----------------------------------------
{
    "network-configs": {
        "test-network": {
            "name": "Test Network",
            "profile": "./connection-profile/test-network.json",
            "enableAuthentication": false
        }
    },
    "license": "Apache-2.0"
}
------------------------------------------------
#   Modify connection profile in the JSON file app/platform/fabric/connection-profile/test-network.json:

$ pico app/platform/fabric/connection-profile/test-network.json

----------------------------------------------------
Change fabric-path to your fabric network disk path in the test-network.json file:
Provide the full disk path to the adminPrivateKey config option, it ussually ends with _sk, for example: /fabric-path/fabric-samples/test - network/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp/keystore/priv_sk
adminUser and adminPassword is the credential for user of Explorer to login the dashboard
enableAuthentication is a flag to enable authentication using a login page, setting to false will skip authentication.

---------------------------------------------------------
Step 14 : Run create database script:

$ cd blockchain-explorer/app/persistence/fabric/postgreSQL/db
$ sudo -u postgres ./createdb.sh

#   Connect to the PostgreSQL database and run DB status commands:

$ sudo -u postgres psql -c '\l'

$ sudo -u postgres psql fabricexplorer -c '\d'

Step 15: Build Hyperledger Explorer

$ cd blockchain-explorer
$ npm install
$ cd client/
$ npm install
$ npm run build

Step 16: Run Hyperledger Explorer

#   Run Locally in Same Location
Modify app/explorerconfig.json to update sync settings.

$ pico app/explorerconfig.json
-----------------------------------------
"sync": {
  "type": "local"
}
----------------------------------------------
$ npm start -----It will have the backend and GUI service up

$ npm run app-stop ----- It will stop the node server

If Hyperledger Fabric network is deployed on other machine, please define the following environment variable

$ DISCOVERY_AS_LOCALHOST=false npm start
--------------------------------------------------
If the Hyperledger Explorer was used previously in your browser be sure to clear the cache before relaunching

$ ./syncstart.sh ------ It will have the sync node up


$ ./syncstop.sh -------- It will stop the sync node

------------------------------------------
Step 16 — Start Hyperledger Explorer
You should be ready to start Explorer.

# To start Hyperledger Explorer

$ docker-compose up -d

# If you changed any config, clear it out with this and start again
$ docker-compose down -v
---------------------------------------
 Hyperledger Explorer should be properly set up and you can access it at http://<Your-IP-Address>:8080. If it prompts you to log in, use exploreradmin:exploreradminpw.

----------------------- 
Configuring  a REST API 

Step -17  The username and password of the dashboard are defined in explorer/first-network.json and to disable the authentication, we can set enableAuthentication to true

$ pico explorer/first-network.json
---------------------------------
 Building your own UI
Step 18 : You can build your own user interface on the top of hyperledger explorer using the REST API exposed by the explorer. Explorer team has provided us the Swagger specifications and you can simply import that into your REST client like Postman  You can find the swagger specification here.

#  Start postman --> Link --> insert https://raw.githubusercontent.com/hyperledger/blockchain-explorer/master/app/swagger.json

# After import the swagger specifications you can see a collection with REST API.

New > Collections 

# And now you can simply use these APIs with any frontend framework of your choice.

-----------------Follow the total procedure on all VM's -----------------
