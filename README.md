# Sana Node

## Usage
[Install docker](https://docs.docker.com/install/) and make sure docker-compose is installed.
```
docker version
docker-compose version
```
Initialize the node with python 3 
```python
python initialize.py
```
Run the node with
```
docker-compose up
```
Run tests
```
docker-compose run web python manage.py test
```
Note: The ipfs container must be terminated manually after the test

## Implementation guidelines 
The backend can be implimented in the following ways:
- Daemon server running in background locally
- On a dedicated computer running as a server

The frontend components can be implimented in the following ways:
- Offline first Web application
- Android application
- iOS application
- GUI Client for Windows, Mac or Linux

# Backend components
The working of the sana node will depend upon these components. The following description is just meant to give orientation to the architecture. 

## CouchDB
CouchDB is a document based NoSQL database that is highly fault tolerant. It's main feature is sync with other applications that use the same Couch protocol. 

There will be syncing on two levels:
- front end application's pouchdb <---> local couch instance
- local couch instance <---> Remote couch instances

The administrator of the local couchDB instance needs to do the following:
1. Create a database named `medblock` with write and read permission for everyone
2. Create `_user` database
3. Create design document in medblocks with following functions:
    - Validation function for medblock format (`ipfs_hash`, `keys`, `user`)
    - Document update restricted to `user`

## IPFS Node
IPFS is a decentralized protocol for file storage. The front end will be able to `add` content to the ipfs node. This can later be retrived with the `cat` command.


## Cluster Management Service worker
The service worker does the following
- IPFS Pinning service orchestration
- Node discovery
- CouchDB Replicator and Sync
 
# Client side implimentation guidelines:
## Data structures
All the data handled by the front end will be abstracted into two main objects: `medblock` and `user`.
## Medblock data structure:
```
{
id: ...,
user: ...,
ipfs_hash : ...,
Keys: {
    [{user: key}, 
    ...]
    } 
}
```
## User data structure:
```
{
id:...,
name:...,
rsa:...,
}
```
## PouchDB:
- All databases can be created locally using [pouchdb.js](https://pouchdb.com/learn.html)

- User and authentication can be managed with [pouch-authentication.js](https://github.com/pouchdb-community/pouchdb-authentication)

- Either set up replication to the backend couchDB instance or directly interact with it 
## WebCrypto
This is to encrypt data before adding to ipfs.
- Provide a RSA key to the user
- Generate random key to encrypt data with AES
- Encrypt the random key asymmetrically with RSA (user specific)
- Add data to ipfs, get `ipfs_hash` and add encrypted key to the `keys` field

## IPFS client
Connect to the ipfs node on the backend using the [IPFS api](https://github.com/ipfs/js-ipfs-api) and add encrypted content.

