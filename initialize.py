import yaml, json
import requests
import time
import subprocess
import os

def load_config():
    with open("config.json","r") as f:
        config = json.load(f)
    return config

def initialize_docker_compose():
     
    docker_compose_yaml = {'services': {'couchdb': {'environment': ['COUCHDB_USER=admin',
                                    'COUCHDB_PASSWORD=admin'],
                                'image': 'couchdb',
                                'ports': ['8001:5984'],
                                'volumes': ['couchdb-data:/opt/couchdb/data']},
                                'db': {'image': 'postgres'},
                                'ipfs': {'image': 'jbenet/go-ipfs'},
                                'rabbit': {'image': 'rabbitmq:alpine'},
                                'redis': {'image': 'redis'},
                                'web': {'build': '.',
                                'command': 'python manage.py runserver 0.0.0.0:8000',
                                'depends_on': ['worker', 'db'],
                                'ports': ['8000:8000'],
                                'volumes': ['.:/code/']},
                                'worker': {'build': '.',
                                'command': 'celery -A tasks worker --loglevel=info',
                                'depends_on': ['rabbit', 'redis'],
                                'volumes': ['.:/code/']}},
                                'version': '3',
                                'volumes': {'couchdb-data': None}}
    return docker_compose_yaml
def wait_for_couch_container():
    while True:
        try:
            if requests.get("http://127.0.0.1:8001/").status_code == 200:
                print("Successfully got CouchDB container!")
                return True
            else:
                print("Non 200 Response")
                return False
        except Exception as e:
            print(e)
            t = 3*attempt
            print("Waiting for container to spin up...{} seconds".format(t))
            time.sleep(t)
            attempt += 1

config = load_config()
docker_compose_yaml = initialize_docker_compose()
if config['prompt']:
    couch_username = "COUCHDB_USER={}".format(input("CouchDB Admin Username: "))
    couch_password = "COUCHDB_PASSWORD={}".format(input("CouchDB Admin Password: "))
    docker_compose_yaml['services']['couchdb']['environment'] = [couch_username, couch_password]

if 'docker-compose.yml' in os.listdir('.'):
    answer = input("[?] Are you sure you want to overwrite the existing docker-compose.yml? (Y/n): ")
    if answer.lower() in ['yes','y']:
        with open("docker-compose.yml","w") as f:
            f.write(yaml.dump(docker_compose_yaml))
    else:
        print("[-] Skipping writing docker-compose.yml")

print("[+] Running 'docker-compose up' as a child process. If this is the first time this may take a long time...")
subprocess.Popen(["docker-compose", "up"], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
attempt = 1

wait_for_couch_container()

print("[+] Destroying containers")
subprocess.Popen(["docker-compose", "down"], shell=True)

# Create medblock database
# create _users database
# Write Validation documents for medblock
    # ipfs_hash, etc etc

# Get ip address of all interfaces (ifaddr.get_adapters())
# Post the ip address on the Django databases (network URL)




couchdb = "http://{}:{}@127.0.0.1/8001".format(couch_username, couch_password)


def create_users():
    return requests.put(couchdb + "_users")

def create_medblocks():
    return requests.put(couchdb + "medblocks")

def create_valitate_medblock():
    validate_medblock = {
    '_id': '_design/validate_medblocks',
    'validate_doc_update': 'function (newDoc, savedDoc, userCtx) {\nfunction require(field, message) {\nmessage = message || "Document must have a " + field;\nif (!newDoc[field]) throw({forbidden : message});\n};\nif (newDoc.type == "medblock") {\nrequire("format");\nrequire("files");\nrequire("keys");\nrequire("user");\n}\n}\n'
    }
    return requests.put(couchdb + "medblocks/_design/validate_medblocks", json=validate_medblock)

def make_fields_public(field):
    return requests.put(couchdb + "_node/nonode@nohost/_config/couch_httpd_auth/public_fields", json=field)