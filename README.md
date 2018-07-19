# Sana Node

## Usage
[Install docker](https://docs.docker.com/install/) and make sure docker-compose is installed.

```
docker version
docker-compose version
```
Run the node with
```
docker-compose up
```
Run tests
```
docker-compose run web python manage.py test
```
Note: The ipfs container must be terminated manually after the test
