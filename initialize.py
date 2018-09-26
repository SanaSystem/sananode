import yaml, json


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

config = load_config()
docker_compose_yaml = initialize_docker_compose()
if config['prompt']:
    couch_username = "COUCHDB_USER={}".format(input("CouchDB Admin Username: "))
    couch_password = "COUCHDB_PASSWORD={}".format(input("CouchDB Admin Password: "))
    docker_compose_yaml['services']['couchdb']['environment'] = [couch_username, couch_password]

with open("docker-compose.yml","w") as f:
    f.write(yaml.dump(docker_compose_yaml))

# Run docker-compose up (Subprocess)

# Create medblock database
# create _users database
# Write Validation documents for medblock
    # ipfs_hash, etc etc

# Get ip address of all interfaces (ifaddr.get_adapters())
# Post the ip address on the Django databases (network URL)


