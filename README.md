# Multicast Menu

Multicast Menu provides a collection of all the multicast video streams available on Internet2 and GEANT.


## Usage
This site can be found at [https://multicastmenu.m2icast.net](https://multicastmenu.m2icast.net). In order for the streams that it links to to run properly on your machine, you will need [VLC 4.0 or later](https://nightlies.videolan.org/) installed.

To view, manually run or see past output of the stream collection scripts used by this site, see the [scripts](https://github.com/Laur04/multicast-menu/tree/master/scripts) folder.


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