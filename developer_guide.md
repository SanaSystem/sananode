# SANA Node Developer’s Guide
# Introduction
This repository has been developed to run on embedded systems called SANA Boxes. It makes use of docker extensively and therefore can run on various platforms like Windows, Mac, Linux with ease. Some of the containers have been specifically made for ARM inorder to run on a Raspberry Pi 3. The following document will describe the installation process and further developoment goals.

# Installation
There are 2 parts to the setup. You first set up a raspberry pi as a SANA Box and then you access it from your client using the frontend.
## SANA Box setup
This installation will assume you are using a freshly set up Raspberry pi and accessing the terminal via SSH as user pi.
Install some prerequesites, Docker, Docker Compose and requests
```
sudo apt install python3-pip git -y
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo usermod -aG docker pi
sudo pip3 install docker-compose
pip3 install requests
```
Test yout docker set up
```
docker run hello-world
docker-compose --version
```
Clone the repository
```
git clone https://github.com/SanaSystem/sananode.git
```
Go into the directory
```
cd sananode
```
Start the initialize script
```
python3 initialize.py
```
This will guide you through the process of setting up the containers for the first run. You can provide it with different values for couchdb password, username in the .env file generated and run again if needed.

Initialize the docker containers
```
docker-compose up -d
```
Ensure that all the containers are running without errors using
```
docker-compose logs
```
Now the raspberry pi is essentially a SANA Box. You can access it from the client.
Just note the IP address of the SANA Box using
```
ifconfig
```
You will need to input it on the client
## Client setup
Clone the repository to the computer you want to access it from
```
git clone https://github.com/SanaSystem/sananode.git
```
Go into the sananode/frontend folder
```
cd sananode/frontend
```
If you have npm and http-server installed, initiate a http server with 
```
http-server
```
Else use python's http server
```
python3 -m http.server
```
Navigate to `http://localhost:8080` to interact with the SANA Node. Input the IP address obtained using `ifconfig` on the SANA Box.

# Structure
4 core technologies are at play to achive sync with other SANA Boxes. They are:
- Docker
- CouchDb
- IPFS
- Django Celery

## Docker
This acts as the base for the rest of the stack to run on. Docker containers are created upon `docker-compose up` using the `docker-compose.yml` file. The environment variables from `.env` is also taken into consideration while building the containers. The `initialize.py` file creates a `.env` file based on the platform - AMD or ARM from `amd.env` and `arm.env` respectively. All the containers are mentioned as services and they can be accessed by other containers by using the name of the service. For example the service named `couchdb` can be accessed from the `web` container by `http://couchdb:<port>`. The ports to be exposed are also mentioned and these will bind to the hosts' ports.
  
## CouchDB
This is a noSQL document based database that is used to store the documents created on the front end. The `config/couchdb.ini` file contains all the configuration details for setting up the database. The username and password can be setup in the .env file.

Everthing in the database can be accessed using simple HTTP. However, there is also a UI available at `http://<ipaddress>:5984/_utils`. This wil be useful to view the documents and make updates more easily.

## IPFS
The ipfs container just runs in the background. A lot of parts are exposed as a part of the UDP hole punching and P2P swarm discovery system. Still, discovery and sync with other nodes are slow, and need to be fixed manually by querying for the ipfs hash from another remote node as soon as its been uploaded to the container.

## Django Celery
This is the heart of where most of the code lies. The whole repository is a django project (although, this is not strictly necessary). Celery has been set up with a `beat` scheduler and a `worker` as services under `django-compose.yml`. The relevant code lies in the `server` module (or folder - in python its the same). Everything that needs to be run at intervals is mentioned in the `tasks.py` file with the decorator `@periodic_task`. The other functions that need to be run asyncromously by the worker threads is created with the `@task` decorator. The tasks can be called with function.delay() in order to run async.

Example:
```
@task
def add():
	return 1+2

def main():
	# Will run async in another container and result will be stored
	return add.delay()
```

The current tasks do the following:
- Check each user in the couchdb database for all their documents
- Compares this documents with that published on the Tangle
- If there is any change in the local document, broadcast the changes to the Tangle (using specific tags mentioning the nature of the data)
- If there is any new updates on the Tangle, update the local database
- All changes must be non destructive (only additions. no deletions)

# Further Development Tasks
The future tasks that need to be implemented are
- Decompose the document to suit the ethereum smart contracts' needs
- Obtain gas automatically from faucet
- Check for updates on ethereum smart contract and local database
- Make changes to the smart contract data if there is any new local change
- Make changes to the local database if new changes on smart contaract data is detected
- Send ipfs hash information to remote IPFS node for faster sync

