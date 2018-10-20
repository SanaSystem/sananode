import json
import time
import subprocess
import os, sys, shutil
import platform

try:
  import requests
except ImportError:
  print("Trying to Install required module: requests")
  os.system('python -m pip install requests')
# -- above lines try to install requests module if not present
# -- if all went well, import required module again ( for global access)
import requests


banner = """
  ____    _    _   _    _      _   _  ___  ____  _____   _          _        
 / ___|  / \  | \ | |  / \    | \ | |/ _ \|  _ \| ____| | |__   ___| |_ __ _ 
 \___ \ / _ \ |  \| | / _ \   |  \| | | | | | | |  _|   | '_ \ / _ \ __/ _` |
  ___) / ___ \| |\  |/ ___ \  | |\  | |_| | |_| | |___  | |_) |  __/ || (_| |
 |____/_/   \_\_| \_/_/   \_\ |_| \_|\___/|____/|_____| |_.__/ \___|\__\__,_|
                                                                             
"""
couchdb_unauth = "http://127.0.0.1:5984/"
def command(sequence):
    if sys.platform == 'linux':
        return ' '.join(sequence)
    else:
        return sequence

def wait_for_couch_container(couchdb_url=couchdb_unauth):
    attempt = 1
    while True:
        try:
            if requests.get(couchdb_url).status_code == 200:
                print("[+] Successfully got CouchDB container!")
                return True
            else:
                print("Non 200 Response")
                return False
        except Exception as e:
            # print(e)
            t = 3*attempt
            print("[o] Waiting for containers to spin up...{} seconds".format(t))
            time.sleep(t)
            attempt += 1

def wait_for_web_container(url="http://localhost:8000/"):
    attempt = 1
    while True:
        try:
            if requests.get(url).status_code == 200:
                print("[+] Successfully got web container!")
                return True
            else:
                print("Non 200 Response")
                return False
        except Exception as e:
            # print(e)
            t = 3*attempt
            print("[o] Waiting for containers to spin up...{} seconds".format(t))
            time.sleep(t)
            attempt += 1 
def get_platform():
    return platform.uname().machine

def initializa_couchdb(couch_username, couch_password):
    couchdb = "http://{}:{}@127.0.0.1:5984/".format(couch_username, couch_password)
    print("[+] Creating _users database")
    print(requests.put(couchdb + "_users").json())
    print("[+] Creating medblocks database")
    requests.put(couchdb + "medblocks")
    print("[+] Creating Design Documents")
    validate_medblock = {
    '_id': '_design/validate_medblocks',
    'validate_doc_update': 'function (newDoc, savedDoc, userCtx) {\nfunction require(field, message) {\nmessage = message || "Document must have a " + field;\nif (!newDoc[field]) throw({forbidden : message});\n};\nif (newDoc.type == "medblock") {\nrequire("format");\nrequire("files");\nrequire("keys");\nrequire("user");\n}\n}\n'
    }
    # requests.put(couchdb + "medblocks/_design/validate_medblocks", json=validate_medblock)
    authenticate_only_user = {
    "_id": "_design/only_user",
    "validate_doc_update": "function(newDoc, oldDoc, userCtx){\r\nif (newDoc.creator.email !== userCtx.name){\r\nthrow({forbidden : \"User must be the same as the one who created this document.\"});\r\n}\r\nif (oldDoc){\r\nif (oldDoc.creator.email !== userCtx.name){\r\nthrow({forbidden: 'User not authorized to modify.'});\r\n}\r\n}\r\n}\r\n"
    }

    # requests.put(couchdb + "medblocks/_design/only_user", json=authenticate_only_user)
    preview_medblock = {
    "_id": "_design/preview",
    "views": {
        "list": {
        "map": "function (doc) {\n  emit(doc.creator.email, {\n    title: doc.title,\n    recipient: doc.recipient,\n    files: doc.files.length\n  });\n}",
        "reduce": "_count"
        }
    },
    "language": "javascript"
    }
    requests.put(couchdb + "medblocks/_design/preview", json=preview_medblock)
    print("Testing initialization...")
    dbs = requests.get(couchdb + "_all_dbs").json()
    # assert(len(dbs) == 2)
    assert('_users' in dbs)
    assert('medblocks' in dbs)

def bootstrap_ipfs():
    # Add bootstrap ip to ipfs bootstrap list
    return 

def copy_env(platform):
    platform = platform[:3].lower()
    if platform not in ['amd', 'arm']:
        print("[-] Not arm or amd...No .env matching .env file found")
        return
    if platform == 'amd':
        print("[+] Copying environment file for AMD")
        shutil.copy('amd.env','.env')
    if platform == 'arm':
        print("[+] Copying environment file for ARM")
        shutil.copy('arm.env','.env')
    

def main():
    print(banner)
    platform = get_platform()
    print("[+] Machine architecture {}".format(platform))
    if '.env' in os.listdir():
        try:
            prompt = input("[?] .env file already present. Overide with defaults?[Y/n]").lower()
        except KeyboardInterrupt:
            print("Interrupter by user. Exiting...")
            exit()
        if prompt in ["y","yes"]:
            copy_env(platform)
    else:
        copy_env(platform)
    
    couch_username, couch_password = "admin", "admin"
    print("[+] Building docker containers")
    subprocess.call(command(["docker-compose","build"]), shell=True)
    print("[+] Running 'docker-compose up' as a child process. If this is the first time this may take a long time...")
    subprocess.Popen(command(["docker-compose", "up"]), shell=True)
    wait_for_web_container()
    print("[+] Running migrations for Django")
    subprocess.call(command(["docker-compose", "exec", "web", "python", "manage.py", "makemigrations"]), shell=True)
    subprocess.call(command(["docker-compose", "exec", "web", "python", "manage.py", "migrate"]), shell=True)
    subprocess.call(command(["docker-compose", "exec", "web", "python", "manage.py", "createsuperuser"]), shell=True)
    wait_for_couch_container()
    print("[+] Initializing couchDB databases")
    try:
        initializa_couchdb(couch_username, couch_password)
    except Exception as e:
        print("[-] Error: {}".format(e))

    print("[+] Destroying containers")
    subprocess.call(command(["docker-compose", "down"]), shell=True)

    # Post the ip address on the Django databases (network URL)
    print("Initialization done. Run node with 'docker-compose up'")

if __name__ == '__main__':
    main()