import yaml, json
import requests
import time
import subprocess
import os, sys
import ifaddr
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
            if requests.get(couchdb_unauth).status_code == 200:
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
def wait_for_web_container():
    attempt = 1
    while True:
        try:
            if requests.get("http://localhost:8000/").status_code == 200:
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
    requests.put(couchdb + "medblocks/_design/validate_medblocks", json=validate_medblock)
    authenticate_only_user = {
    "_id": "_design/only_user",
    "validate_doc_update": "function(newDoc, oldDoc, userCtx){\r\nif (newDoc.creator.email !== userCtx.name){\r\nthrow({forbidden : \"User must be the same as the one who created this document.\"});\r\n}\r\nif (oldDoc){\r\nif (oldDoc.creator.email !== userCtx.name){\r\nthrow({forbidden: 'User not authorized to modify.'});\r\n}\r\n}\r\n}\r\n"
    }

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
    # Create Preview


    
    ## TO DO

    requests.put(couchdb + "medblocks/_design/only_user", json=authenticate_only_user)
    print("Testing initialization...")
    dbs = requests.get(couchdb + "_all_dbs").json()
    # assert(len(dbs) == 2)
    assert('_users' in dbs)
    assert('medblocks' in dbs)

def get_ip():
    print("[+] Scanning IP on all available interfaces")
    results = [(adaptor.nice_name, adaptor.ips[-1].nice_name, adaptor.ips[-1].ip) for adaptor in ifaddr.get_adapters()]
    print("[+] Found {} interfaces".format(len(results)))
    data = [("Interface", "Name", "IP address")] + results
    for i, d in enumerate(data):
        line = '|'.join(str(x).ljust(45) for x in d)
        print(line)
        if i == 0:
            print('-' * len(line))
    public_ip = requests.get("http://ip.42.pl/raw").text
    print("Public IP from ip.42.pl: {}".format(public_ip))
    ip_list = [adaptor[2] for adaptor in results]
    if public_ip not in ip_list:
        print("-!-!- None of the interfaces match the Public IP. You will need to set up port forwarding to enable access outside the network -!-!-")
    if input("Would you like to register your public IP {}?".format(public_ip)).lower() in ['yes','y']:
        register_ip = public_ip
    else:
        register_ip = input("Please enter the IP address you want to configuire this SANA Node with (eg:{}): ".format(ip_list[0]))
    print("[+] Registering node...")
    bootstrap_url = "http://68.183.18.129:8000/nodes/"
    r = requests.post(bootstrap_url, json={"ipAddress":register_ip, "couchReplication":True, "ipfsReplication":False})
    if r.status_code == 201:
        print("[+] Registered {} successfully".format(r.json()['ipAddress']))

def main():
    print(banner)
    print("[+] Loading configuration from config.json")
    config = load_config()
    docker_compose_yaml = initialize_docker_compose()
    couch_username, couch_password = "admin", "admin"

    if config['prompt']:
        print("[o] Set up your couchDB username and Password")
        couch_username = input("CouchDB Admin Username: ")
        couch_password = input("CouchDB Admin Password: ")
        couch_username_env = "COUCHDB_USER={}".format(couch_username)
        couch_password_env = "COUCHDB_PASSWORD={}".format(couch_password)
        docker_compose_yaml['services']['couchdb']['environment'] = [couch_username_env, couch_password_env]
        
    print("[+] Attempting to write docker-compose.yaml")
    write_docker_compose(docker_compose_yaml)
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
    get_ip()


    # Post the ip address on the Django databases (network URL)
    

    print("Initialization done. Run node with 'docker-compose up'")

if __name__ == '__main__':
    main()