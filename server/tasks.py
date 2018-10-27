from celery import shared_task, task
from .utils import decompose_medblocks, to_set, to_dict_list, reconstruct_medblocks
from .blockchain import retrieve_from_tangle, broadcast_on_tangle
import couchdb
import requests
import json

@shared_task
def async_broadcast_on_tangle(list_of_elements):
    return broadcast_on_tangle(list_of_elements)

@task
def check_iota_sync(email, base_url="http://couchdb:5984/"):
    # list all documents associated with user
    server = couchdb.Server(base_url)
    db = server['medblocks']
    docs = [db[medblock.id] for medblock in db.view('preview/patient', key=email)]

    # Decompose document into constituants
    
    db_medfrags = to_set(decompose_medblocks(docs))
    
    
    # Get all associated transactions with address
    iota_medfrags = to_set(retrieve_from_tangle(email))

    transmit_to_iota = db_medfrags - iota_medfrags
    # print(transmit_to_iota)
    # print("Printing Difference set")
    # print([i['tag'] for i in to_dict_list(transmit_to_iota)])

    reconstruction_medfrags = iota_medfrags | db_medfrags
    reconstruction_medfrags = to_dict_list(reconstruction_medfrags)
    new_documents = reconstruct_medblocks(reconstruction_medfrags)

    # include _rev
    print("Newly constructed docs...")
    print(new_documents)
    for i in range(len(new_documents)):
        id = new_documents[i]['_id']
        try:
            new_documents[i]['_rev'] = db['_id'].rev
        except couchdb.http.ResourceNotFound:
            pass
        new_documents[i] = couchdb.Document(new_documents[i])

    # print(new_documents)
    print(len(new_documents))
    print("Updating {} documents on the database".format(len(new_documents)))
    db.update(new_documents)
    print("Transmitting {} elements to the tangle".format(len(transmit_to_iota)))
    async_broadcast_on_tangle.delay(to_dict_list(transmit_to_iota))
    return

@task 
def check_sync(email):
    # Check IPFS sync

    # Check Pin status
    pass

@task
def trigger_sync(email):
    pass




