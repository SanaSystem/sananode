from celery import shared_task, task
from celery.task.schedules import schedule
from celery.decorators import periodic_task
from .utils import decompose_medblocks, to_set, to_dict_list, reconstruct_medblocks, remove_duplicates, approved_decompose_medblocks
from .blockchain import retrieve_from_tangle, broadcast_on_tangle, server
import couchdb
from sananode.settings import COUCHDB_ADMIN_BASE_URL
from server.models import SyncParameters
import requests
import json
import time
import ipfsapi
from django.core.cache import cache

LOCK_EXPIRE = 60 * 5

@shared_task
def async_broadcast_on_tangle(list_of_elements):
    result = broadcast_on_tangle(list_of_elements)
    if len(result) > 0:
        return True
    else:
       return False

@task
def check_iota_sync(email):
    # list all documents associated with user
    

    
            db = server['medblocks']
            results, iota_new = retrieve_from_tangle(email)
            simple_sync = True
            if simple_sync:
                docs = [db[medblock.id] for medblock in db.view('preview/patient', key=email)]
                db_medfrags = to_set(approved_decompose_medblocks(docs))
                iota_medfrags = to_set(results)
                transmit_to_iota = db_medfrags - iota_medfrags
                print("DB MEDFRAGS: {} , IOTA MEDFRAGS: {}".format(len(db_medfrags), len(iota_medfrags)))
                db_update = len(iota_medfrags - db_medfrags) > 0
                
                if len(transmit_to_iota) > 0:
                    print("Transmitting {} transaction to IOTA".format(len(transmit_to_iota)))
                    broadcast_on_tangle(to_dict_list(transmit_to_iota))
                if db_update:
                    print("Difference {}".format(iota_medfrags - db_medfrags))
                    reconstruction_medfrags = iota_medfrags | db_medfrags
                    reconstruction_medfrags = to_dict_list(reconstruction_medfrags)
                    new_documents = reconstruct_medblocks(reconstruction_medfrags)
                    print("Updating {} documents on the database".format(len(new_documents)))
                    for doc in new_documents:
                        id = doc['_id']
                        doc = couchdb.Document(doc)
                        try:
                            old_document = db[id]
                            doc['_rev'] = old_document.rev
                            db.save(doc)
                        except couchdb.http.ResourceNotFound:
                            db[id] = doc
                return True
        

def check_ipfs_sync(email):
    db = server['medblocks']
    results = db.view('preview/ipfshashes', key=email)
    hashes = [r.value for r in results]
    for hash in hashes:
        check_ipfs_file.delay(hash)

@task
def check_ipfs_file(hash):
    print("Syncing ipfs hash {}".format(hash))
    client = ipfsapi.Client("ipfs", 5001)
    client.cat(hash)
    requests.get("https://ipfs.infura.io/ipfs/{}/".format(hash))
    requests.get("https://ipfs.infura.io:5001/api/v0/pin/add?arg=/ipfs/{}".format(hash))
    requests.get("http://ipfs.io/ipfs/{}/".format(hash))
    return

@periodic_task(run_every=5, name="Sync IOTA", ignore_result=True)
def check_all_users():
    lock_id = "checkiotasync"
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)
    if acquire_lock():
        try:
            db = couchdb.Server(COUCHDB_ADMIN_BASE_URL)['_users']
            emails = [i.key for i in db.view('preview/list')]
            emails = remove_duplicates(emails)
            for email in emails:
                print("Checking for :{}".format(email))
                check_iota_sync(email)
                # check_ipfs_sync(email)
        finally:
            release_lock()

