from celery import shared_task, task
from celery.task.schedules import schedule
from celery.decorators import periodic_task
from .utils import decompose_medblocks, to_set, to_dict_list, reconstruct_medblocks, remove_duplicates
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
    lock_id = "checkiotasync-lock-{}".format(email)
    acquire_lock = lambda: cache.add(lock_id, "true", LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)

    if acquire_lock():
        try:
            db = server['medblocks']
            results, iota_new = retrieve_from_tangle(email)
            try:
                current_params = SyncParameters.objects.get(pk=1)
            except SyncParameters.DoesNotExist:
                print("[o] Creating Empty Sync parameters")
                current_params = SyncParameters.objects.create(pk=1, seq='1')

            last_seq = db.changes()['last_seq']
            print("Current stored seq: {}...".format(current_params.seq[:20]))
            if last_seq == current_params.seq:
                print("[o] Nothing new in medblocks")
                db_new = False
            else:
                print("[+] New changes in medblocks")
                db_new = True
            if db_new or iota_new:
                print("[+] State changed. Getting ready...")
                docs = [db[medblock.id] for medblock in db.view('preview/patient', key=email)]
                db_medfrags = to_set(decompose_medblocks(docs))
                iota_medfrags = to_set(results)

            if db_new: 
                print("[+] State change detected in medblocks database. Broadcasting messages on IOTA")
                transmit_to_iota = db_medfrags - iota_medfrags
                print("Transmitting {} elements to the tangle".format(len(transmit_to_iota)))
                result = async_broadcast_on_tangle.delay(to_dict_list(transmit_to_iota))
                if result.wait():
                    print("Updating seq value to {}".format(last_seq))
                    current_params.seq = last_seq
                    current_params.save()
                    return True
                else:
                    time.sleep(0.5)
            
            if iota_new:
                print("[+] State change detected in IOTA transactions. Updating documents")
                reconstruction_medfrags = iota_medfrags | db_medfrags
                reconstruction_medfrags = to_dict_list(reconstruction_medfrags)
                new_documents = reconstruct_medblocks(reconstruction_medfrags)
                for i in range(len(new_documents)):
                    id = new_documents[i]['_id']
                    try:
                        new_documents[i]['_rev'] = db['_id'].rev
                    except couchdb.http.ResourceNotFound:
                        pass
                    new_documents[i] = couchdb.Document(new_documents[i])
                print("Updating {} documents on the database".format(len(new_documents)))
                db.update(new_documents)
            return True
        finally:
            release_lock()
        print("Another instance running...")
        return

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
    db = couchdb.Server(COUCHDB_ADMIN_BASE_URL)['_users']
    emails = [i.key for i in db.view('preview/list')]
    emails = remove_duplicates(emails)
    for email in emails:
        print("Checking for :{}".format(email))
        check_iota_sync(email)
        check_ipfs_sync(email)



