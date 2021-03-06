# E--Med-Block-Chain

Seting Up IPFS Private Network 

By default, IPFS and IPFS-Cluster use the following ports:

IPFS
4001 – Communication with other nodes
5001 – API server
8080 – Gateway server > change it to 3000
IPFS-CLUSTER
9094 – HTTP API endpoint
9095 – IPFS proxy endpoint
9096 – Cluster swarm, used for communication between cluster nodes

To run this experiment I have created two virtual machines with installed Linux Ubuntu Distributive version 18.04 LTS and command line as the main tool for installing necessary packages and settings. 
Let’s suppose that we have three VMs with the following IP addresses:
to check use

$ ifconfig

Node0: 192.168.56.101 ---- change accordingly 
Node1: 192.168.195.3 ---- Change accordingly 

Let’s start with the zero node (Node0) which will be our bootstrap node.

Step -1 Install IPFS
We will install the latest version of the go-ipfs. At the moment of writing this article, it was v0.10.0 for Linux. You can check for the latest version here https://dist.ipfs.io/#go-ipfs

Download IPFS, unzip tar file, move unzipped folder under bin and initialise IPFS node:
$ wget https://dist.ipfs.io/go-ipfs/v0.10.0/go-ipfs_v0.10.0_linux-amd64.tar.gz
$ tar xvfz go-ipfs_v0.4.18_linux-amd64.tar.gz

$ sudo mv go ipfs/ipfs /usr/local/bin/ipfs

$ ipfs init --profile server ** ---- Use only once do not sudo** 

$ ipfs version

----Install IPFS on all VMS ---------------------------------

Step 2 Creating a Private network
Once you have Go and IPFS installed on all of your nodes, run the following command to install the swarm key generation utility. Swarm key allows us to create a private network and tell network peers to communicate only with those peers who share this secret key

$ echo -e “/key/swarm/psk/1.0.0/\n/base16/\n `tr -dc ‘a-f0–9’ < /dev/urandom | head -c64`” > ~/.ipfs/swarm.key

Copy the file generated swarm.key to the IPFS directory of each node participating in the private network. First of all, you need to remove the default entries of bootstrap nodes from all the nodes you have created.

Copy the generated swarm file to the .ipfs directory of all client nodes.

From Node0 home directory

$ cd .ipfs/
$ cat swarm.key
/key/swarm/psk/1.0.0/
/base16/
25f64b1cf31f649817d495e446d4cbcc99000b8cc032a89b681e5f86f995fa28

On node1, create swarm.key in /home/ipfs/.ipfs

$ nano swarm.key

Add to file the 3 lines from node0 swarm.key:
---------------------------------------------------------------
/key/swarm/psk/1.0.0/
/base16/
25f64b1cf31f649817d495e446d4cbcc99000b8cc032a89b681e5f86f995fa28
-----------------------------------------------------------------------

Step 3: Bootstrapping IPFS nodes

$ ipfs bootstrap 

check all the nodes

$ ipfs bootstrap rm –all

$ ipfs config show | grep "Bootstrap"

$ ipfs id ---- to get the hash key 

Add the hash address of your bootstrap to each of the nodes including the bootstrap.

ipfs bootstrap add /ip4/192.168.56.101/tcp/4001/ipfs/QmQVvZEmvjhYgsyEC7NvMn8EWf131EcgTXFFJQYGSz4Y83

The IP part (192.168.56.101) will be changed to your Node0 machine IP. The last part is the peer ID which is generated when you initialise your peer ipfs init). You can see it above where it shows “peer identity

$ ipfs id ---- to get the hash key 

	Example  : QmQVvZEmvjhYgsyEC7NvMn8EWf131EcgTXFFJQYGSz4Y83

We also need to set the environment variable “LIBP2P_FORCE_PNET” to force our network to Private mode:

$ export LIBP2P_FORCE_PNET=1

Step 4 :  Configuring IP for communication 

Inside the .ipfs folder, there is a “config” file. It contains a lot of settings including the network details on which our IPFS nodes will work on. Open this config file and find “Addresses”. It will look like this:

--------------------------------------------
"Addresses": {

"API": "/ip4/192.168.56.101/tcp/5001",

"Announce": [],

"Gateway": "/ip4/192.168.56.101/tcp/3000",

"NoAnnounce": [],

"Swarm": [

"/ip4/0.0.0.0/tcp/4001",

"/ip6/::/tcp/4001"

]

},
-----------------------------------------
The IP mentioned in the API is the one on which IPFS will bind on for communication. By default, it’s localhost (127.0.0.1), so to enable our nodes to “see” each other we need to set this parameter accordingly to each node’s IP. Gateway parameter is for access from the browser.

Step 5 : Start the nodes and test

We are done with all the configurations, and now it is time to start all the nodes to see if everything went well and if they are closed to the private network. Run IPFS daemon on all of your nodes.

$ Ipfs daemon 

You should see the contents of the added file from the first node. To check and be sure that we have a private network we can try to access our file by its CID from the public IPFS gateway. You can choose one of the public gateways from this list: https://ipfs.github.io/public-gateway-checker.

If you did everything right, then the file won’t be accessible. Also, you can run the ipfs swarm peers command, and it will display a list of the peers in the network it’s connected to. In our example, each peer sees two others.

Step 6: Run IPFS daemon as a service in the background

For  IPFS demon to be continually running, even after we have exited from our console session, we will create systemd service. Before we do so, stop/kill your ipfs daemon. Create a file for a new service.

$ sudo nano /etc/systemd/system/ipfs.service

And add to it the following settings:
---------------------------------------------------------------------------------------
[Unit]

 Description=IPFS Daemon

 After=syslog.target network.target remote-fs.target nss-lookup.target

 [Service]

 Type=simple

 ExecStart=/usr/local/bin/ipfs daemon --enable-namesys-pubsub

 User=root

 [Install]

 WantedBy=multi-user.target
-----------------------------------------------------------------------------------------------
Save and close the file.
Apply the new service.

$ sudo systemctl daemon-reload

$ sudo systemctl enable ipfs

$ sudo systemctl start ipfs

$ sudo systemctl status ipfs

Reboot your system and check that IPFS daemon is active and running, and then you can again try to add the file from one node and access it from another.

We have completed part of creating a private IPFS network and running its demons as a service. At this phase, you should have two IPFS nodes organised in one private network. Now let’s create our IPFS-CLUSTER for data replication.
--------------------------------------------------------------------------------------------------

IPFS Cluster 

After we create a private IPFS network, we can start deploying IPFS-Cluster on top of IPFS for automated data replication and better management of our data.

The method we are following is  – to bootstrap nodes (you can add new peers after cluster was created).

IPFS-Cluster includes two components:

ipfs-cluster-service mostly to initialise cluster peer and run its daemon
ipfs-cluster-ctl for managing nodes and data among the cluster

Step 1: Install IPFS-Cluster

There are many ways how to install IPFS-Cluster. In this manual, we are using the installing from source method. You can see all the provided methods here.

Run next commands in your console terminal to install ipfs-cluster components:


$ git clone https://github.com/ipfs/ipfs-cluster.git 
$ GOPATH/src/github.com/ipfs/ipfs-cluster
cd $GOPATH/src/github.com/ipfs/ipfs-cluster
make install

Check successful installation by running:


$  ipfs-cluster-service --version

$  ipfs-cluster-ctl --version

Repeat this step for all of your nodes.

Step 2: Generate and set up CLUSTER_SECRET variable

Now we need to generate CLUSTER_SECRET and set it as an environment variable for all peers participating in the cluster. Sharing the same CLUSTER_SECRET allow peers to understand that they are part of one IPFS-Cluster. We will generate this key on the zero node and then copy it to all other nodes. On your first node run the following commands:


export CLUSTER_SECRET=$(od -vN 32 -An -tx1 /dev/urandom | tr -d ' \n')   echo $CLUSTER_SECRET

You should see something like this:


9a420ec947512b8836d8eb46e1c56fdb746ab8a78015b9821e6b46b38344038f

In order for CLUSTER_SECRET to not disappear after you exit the console session, you must add it as a constant environment variable to the .bashrc file. Copy the printed key after echo command and add it to the end of .bashrc file on all of your nodes.

It should look like this:


export CLUSTER_SECRET=9a420ec947512b8836d8eb46e1c56fdb746ab8a78015b9821e6b46b38344038f

And don’t forget to update your .bashrc file with command:

$ source ~/.bashrc

Step 3: Init and Start cluster

After we have installed IPFS-Cluster service and set a CLUSTER_SECRET environment variable, we are ready to initialise and start first cluster peer (Node0).

Note: make sure that your ipfs daemon is running before you start the ipfs-cluster-service daemon. To initialise cluster peer, we need to run the command:


$ -cluster-service init

To start cluster peer, run:


$ -cluster-service daemon

You should see the output in the console:

INFO cluster: IPFS Cluster is ready cluster.go:461

$ ipfs-cluster-service daemon

You should see the output in the console:


INFO cluster: IPFS Cluster is ready cluster.go:461

Now open a new console window and connect to your second VM(node1). Note: make sure that your ipfs daemon is running before you start the ipfs-cluster-service daemon.

You need to install IPFS-Cluster components and set a CLUSTER_SECRET environment variable (copy from node0) as we did it for our first node. Run the following commands to initialise IPFS-Cluster and bootstrap it to node0:


$ ipfs-cluster-service init

$ ipfs-cluster-service daemon --bootstrap

/ip4/192.168.56.101/tcp/9096/ipfs/QmZjSoXUQgJ9tutP1rXjjNYwTrRM9QPhmD9GHVjbtgWxEn

The IP part (192.168.56.101) will be changed to your Node0 machine IP. The last part is the cluster peer ID which is generated when you initialise your cluster peer(ipfs-cluster-service init). Bear in mind that it should be IPFS-Cluster peer ID, not an IPFS peer ID.

You can run ipfs-cluster-service id command in the console to get this. You need to change IP and cluster peer ID according to your Node0. Do this for all of your nodes. To check that we have two peers in our cluster, run command:


$ Ipfs-cluster-ctl peers ls

And you should see the list of cluster peers:

-------------------------------------------------------------------
node1 & > ipfs-cluster-ctl peers ls

QmYFYwnFUkjFhJcSJJGN72wwedZnpQQ4aNpAtPZt8g5fCd | Sees 1 other peers

Addresses:

/ip4/127.0.0.1/tcp/10096/ipfs/QmYFYwnFUkjFhJcSJJGN72wwedZnpQQ4aNpAtPZt8g5fCd

/ip4/192.168.1.3/tcp/10096/ipfs/QmYFYwnFUkjFhJcSJJGN72wwedZnpQQ4aNpAtPZt8g5fCd

IPFS: Qmaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

/ip4/127.0.0.1/tcp/4001/ipfs/Qmaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

/ip4/192.168.1.3/tcp/4001/ipfs/Qmaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa

QmZjSoXUQgJ9tutP1rXjjNYwTrRM9QPhmD9GHVjbtgWxEn | Sees 1 other peers

Addresses:

/ip4/127.0.0.1/tcp/9096/ipfs/QmZjSoXUQgJ9tutP1rXjjNYwTrRM9QPhmD9GHVjbtgWxEn

/ip4/192.168.1.2/tcp/9096/ipfs/QmZjSoXUQgJ9tutP1rXjjNYwTrRM9QPhmD9GHVjbtgWxEn

IPFS: Qmbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb

/ip4/127.0.0.1/tcp/4001/ipfs/Qmbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb

/ip4/192.168.1.2/tcp/4001/ipfs/Qmbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb

--------------------------------------------------------------------------------
Repeat this step for the second node and all others nodes you want to join to the cluster.

Step 4: Run IPFS-Cluster daemon as a service

For the IPFS-Cluster daemon to be continually running, even after we close console session, we will create systemd service for it. Run the following command to create a file for IPFS-Cluster system service:


$  sudo nano /etc/systemd/system/ipfs-cluster.service

And insert to it:
------------------------------------------------------

[Unit]

Description=IPFS-Cluster Daemon

Requires=ipfs

After=syslog.target network.target remote-fs.target nss-lookup.target ipfs

[Service]

Type=simple

ExecStart=/home/ubuntu/gopath/bin/ipfs-cluster-service daemon

User=root

[Install]

WantedBy=multi-user.target
----------------------------------------------------------
Apply new service and run it:


$ sudo systemctl daemon-reload

$ sudo systemctl enable ipfs-cluster

$ sudo systemctl start ipfs-cluster

$ sudo systemctl status ipfs-cluster


Reboot your machine and check that both IPFS and IPFS-Cluster services are running.

Step 5: Test IPFS-Cluster and data replication

To test data replication, create the file and add it to the cluster:

$ ipfs-cluster-ctl add Tejamedical.txt

Take CID of the recently added file and check its status:
$ ipfs-cluster-ctl status CID

You should see that this file has been PINNED among all cluster nodes.
-----------------------------------------------------------------------------------
References 
https://labs.eleks.com/2019/03/ipfs-network-data-replication.html
