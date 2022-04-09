# Multicast Menu API

Multicast Menu provides an API to add streams to the site.


## Setup
For the time being, each user of the API must recieve a unique identifier in order to be able to send streams. Contact an admin for one.


## Usage


## Add inside
requests.post("http://beethoven.csl.tjhsst.edu/api/add/", data={"unique_identifier":"test", "source":"198.38.15.46", "group":"198.38.15.77", "inside_request":"True"}).content


## Remove inside
requests.post("http://beethoven.csl.tjhsst.edu/api/remove/", data={"unique_identifier":"test", "access_code":"8ZMXL14MLAh0pQ7NTcGYZOCBRrOhg3GaY9X0y4bW"}).content

## Add API
requests.post("http://beethoven.csl.tjhsst.edu/api/add/", data={"unique_identifier":"test", "source":"198.38.15.46", "group":"198.38.15.77"}).content

## Remove API
requests.post("http://beethoven.csl.tjhsst.edu/api/remove/", data={"unique_identifier":"test", "access_code":"8ZMXL14MLAh0pQ7NTcGYZOCBRrOhg3GaY9X0y4bW"}).content
