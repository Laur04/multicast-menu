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
Migrate and run the development server.

```bash
cd ~/multicast-menu
python manage.py migrate
python manage.py makemigrations
```

Visit [localhost:8000](localhost:8000) to view the local copy of the site.


## Contributing
Pull requests and feature suggestions are welcome.