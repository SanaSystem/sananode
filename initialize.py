import yaml, json
import requests
import time
import subprocess
import os, sys
banner = """
  ____    _    _   _    _      _   _  ___  ____  _____   _          _        
 / ___|  / \  | \ | |  / \    | \ | |/ _ \|  _ \| ____| | |__   ___| |_ __ _ 
 \___ \ / _ \ |  \| | / _ \   |  \| | | | | | | |  _|   | '_ \ / _ \ __/ _` |
  ___) / ___ \| |\  |/ ___ \  | |\  | |_| | |_| | |___  | |_) |  __/ || (_| |
 |____/_/   \_\_| \_/_/   \_\ |_| \_|\___/|____/|_____| |_.__/ \___|\__\__,_|
                                                                             
"""

def command(sequence):
    if sys.platform == 'linux':
        return ' '.join(sequence)
    else:
        return sequence

def load_config():
    with open("config.json","r") as f:
        config = json.load(f)
    return config

def initialize_docker_compose():
    with open("docker-compose.yml.sample", "r") as f:
        docker_compose_yaml = yaml.load(f.read())
        return docker_compose_yaml

def wait_for_couch_container():
    attempt = 1
    while True:
        try:
            if requests.get("http://127.0.0.1:8001/").status_code == 200:
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

def write_docker_compose(yaml_data):
    if 'docker-compose.yml' in os.listdir('.'):
        answer = input("[?] Are you sure you want to overwrite the existing docker-compose.yml? (Y/n): ")
        if answer.lower() not in ['yes','y']:
            print("[-] Skipping writing docker-compose.yml")
            return
    with open("docker-compose.yml","w") as f:
        print("[+] Writing docker-compose.yml")
        f.write(yaml.dump(yaml_data))

def initializa_couchdb(couch_username, couch_password):
    couchdb = "http://{}:{}@127.0.0.1:8001/".format(couch_username, couch_password)
    print("[+] Creating _users database")
    print(requests.put(couchdb + "_users").json())
    print("[+] Creating medblocks database")
    requests.put(couchdb + "medblocks")
    print("[+] Creating Design Documents")
    validate_medblock = {
    '_id': '_design/validate_medblocks',
    'validate_doc_update': 'function (newDoc, savedDoc, userCtx) {\nfunction require(field, message) {\nmessage = message || "Document must have a " + field;\nif (!newDoc[field]) throw({forbidden : message});\n};\nif (newDoc.type == "medblock") {\nrequire("format");\nrequire("files");\nrequire("keys");\nrequire("user");\n}\n}\n'
    }
    requests.put(couchdb + "medblocks/_design/validate_medblocks", json=validate_medblock)
    authenticate_only_user = {
        '_id':'_design/only_user',
        'validate_doc_update': "function (newDoc, savedDoc, userCtx) {\nfunction require(field, message) {\nmessage = message || \"Document must have a \" + field;\nif (!newDoc[field]) throw({forbidden : message});\n};\nif (newDoc.type == \"medblock\") {\nrequire(\"format\");\nrequire(\"files\");\nrequire(\"keys\");\nrequire(\"user\");\n}\n}\n"
    }
    requests.put(couchdb + "medblocks/_design/only_user", json=authenticate_only_user)
    print("[+] Making email user field public")
    requests.put(couchdb + "_node/nonode@nohost/_config/couch_httpd_auth/public_fields", json="email")
    print("[+] Making rsa user field public")
    requests.put(couchdb + "_node/nonode@nohost/_config/couch_httpd_auth/public_fields", json="rsa")
    print("Testing initialization...")
    dbs = requests.get(couchdb + "_all_dbs").json()
    assert(len(dbs) == 2, "More than two databases found!")
    assert('_users' in dbs)
    assert('medblocks' in dbs)

def main():
    print(banner)
    print("[+] Loading configuration from config.json")
    config = load_config()
    docker_compose_yaml = initialize_docker_compose()
    couch_username, couch_password = "admin", "admin"

    if config['prompt']:
        print("[o] Set up your couchDB username and Password")
        couch_username = "COUCHDB_USER={}".format(input("CouchDB Admin Username: "))
        couch_password = "COUCHDB_PASSWORD={}".format(input("CouchDB Admin Password: "))
        docker_compose_yaml['services']['couchdb']['environment'] = [couch_username, couch_password]
    print("[+] Attempting to write docker-compose.yaml")
    write_docker_compose(docker_compose_yaml)
    print("[+] Building docker containers")
    subprocess.call(command(["docker-compose","build"]), shell=True)
    print("[+] Running 'docker-compose up' as a child process. If this is the first time this may take a long time...")
    subprocess.Popen(command(["docker-compose", "up"]), shell=True)

    wait_for_couch_container()
    print("[+] Running migrations for Django")
    subprocess.call(command(["docker-compose", "exec", "web", "python", "manage.py", "makemigrations"]), shell=True)
    subprocess.call(command(["docker-compose", "exec", "web", "python", "manage.py", "migrate"]), shell=True)
    
    print("[+] Initializing couchDB databases")
    try:
        initializa_couchdb(couch_username, couch_password)
    except Exception as e:
        print("[-] Error: {}".format(e))

    print("[+] Destroying containers")
    subprocess.call(command(["docker-compose", "down"]), shell=True)

    # Create medblock database
    # create _users database
    # Write Validation documents for medblock
        # ipfs_hash, etc etc

    # Get ip address of all interfaces (ifaddr.get_adapters())
    # Post the ip address on the Django databases (network URL)
    

    print("Initialization done. Run node with 'docker-compose up'")
main()