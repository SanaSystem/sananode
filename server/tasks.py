from celery import shared_task, task
from .utils import decompose_medblocks, to_set
from .blockchain import retrieve_from_tangle
import requests
import json


        
@task
def check_iota_sync(email):
    # list all documents associated with user
    """
    requests.get("_degign/preview/...?key=email")
    """
    # Decompose document into constituants
    
    db = decompose_medblocks
    
    # Get all associated transactions with address
    iota_db = retrieve_from_tangle

    transmit_to_iota = iota_db - db

    reconstruct_new_document = iota_db + db

    # Trigger iota update
    broadcast_on_tangle.delay(transmit_to_iota)

    # Trigger couchdb update
    """
    get(id)
    put(id, rev)
    """
    pass

@task 
def check_sync(email):
    # Check IPFS sync

    # Check Pin status
    pass

@task
def trigger_sync(email):
    pass




