# Multicast Menu API

Multicast Menu provides an API to add streams to the site.


## Setup
For the time being, each user of the API must recieve a unique identifier in order to be able to send streams. Contact an admin for one.


## Usage


## Add inside
requests.post("http://beethoven.csl.tjhsst.edu/api/add/", data={"unique_identifier":"test", "source":"198.38.15.46", "group":"198.38.15.77", "inside_request":"True"}).content


## Remove inside
