from celery import shared_task, task
import requests
from initialize import wait_for_couch_container
@shared_task
def add(x,y):
    return x+y

@shared_task
def setUpReplication(nodeIp):
    # CouchDb 2 way continuous replication
    
    couchdb_url = "http://admin:admin@68.183.18.129:5984/"
    
    if wait_for_couch_container(couchdb_url):
        print("Creating 2 way replication...")
        r = requests.post(couchdb_url + "_replicate", json= {
            "source": "http://{}:5984/medblocks/".format(nodeIp),
            "target": couchdb_url + "medblocks/",
            "coutinious": True
        })
        if r.json()['ok'] == 'true':
            return True
    return False

@task
def checkSync(nodeIp):
    # Check IPFS sync

    # Check Pin status

    # Check CouchDB sync

    # Check Blockchain sync
    pass


@task
def checkKeys(nodeIp):

    # Check couchDB database with blockchain database

    # Detele if keys are written to blockchain

    pass


