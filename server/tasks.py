from celery import shared_task, task
import requests
@shared_task
def add(x,y):
    return x+y

def decompose_medblock(medblock):
    pass

@task
def check_iota_sync(email):
    # list all documents associated with user
    medblocks_on_disk = []
    # Decompose document into constituants
    decomposed_medblocks_on_disk = [[], [], []]
    # Get associated registered addresses on IOTA
    
    # Get all associated transactions with address

    # Decode txns
    decomposed_medblocks_on_iota = [[], [], []]

    # set.symmetric_difference, from where to where

    # Trigger iota update

    # Trigger couchdb update

    pass

@task 
def check_ipfs_sync(email):
    # Check IPFS sync

    # Check Pin status
    pass

@task
def trigger_sync(email):
    pass




