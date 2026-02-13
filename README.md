# Multicast Menu

Multicast Menu provides a collection of all the multicast video streams available on Internet2 and GEANT.


## Usage
This site can be found at [https://menu.m2icast.net](https://menu.m2icast.net). In order for the streams that it links to to run properly on your machine, you will need [VLC 4.0 or later](https://nightlies.videolan.org/) installed.

To manually run the stream collection scripts used by this site, see the [multicast/stream_collection_scripts](https://github.com/Laur04/multicast-menu/tree/master/multicast/stream_collection_scripts) folder.


## API
To use the API, you must register your sending server and recieve a unique ID to send with your requests. See API.md.


## Development
Clone this repository.

```bash
git clone https://github.com/Laur04/multicast-menu.git ~/multicast-menu
```
Migrate and run the development server using docker compose.

```bash
cd ~/multicast-menu
docker compose -f dev-env/docker-compose.yml up -d
```

Visit [localhost:80](localhost:80) to view the local copy of the site.

The application will automatically update when code changes are made. When making changes to databases, static files or settings, run `docker restart application` to run migrations, collect the static files and/or restart the server.

Note that running `docker compose -f dev-env/docker-compose.yml down` will fully tear down and remove the containers. This will delete the postgres database. You can avoid this by removing lines 5-15 from `multicast-menu/multicast/settings/secret.py` *before* running the docker compose `up` command. This will move the database into a local file that will persist through tearing down and reestablishing the containers. Either database will be seeded with dummy data and an admin superuser `(admin/admin123)` when it is first set up. Whenever the application container is restarted, it will attempt to reseed the dummy data if the absense of a user with the username `admin` is detected.


## Contributing
Pull requests and feature suggestions are welcome.