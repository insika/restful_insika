## RESTful INSIKA HTTP Test Server ##

simple python testserver for the RESTful INSIKA Interface


NOTE: This standalone server is designed for development and conformance tests on application level only. Do not use in productive environments!

This example relies on web.py and has been tested to work with version web.py-0.37.

### Preparation ###

To get started, make sure you have Python 2.x.y installed. 
After typing `python` you should see something like this: 
`Python 2.7.3 on linux2. Type "help", "copyright", "credits" or "license" for more information. >>>`
If you don't have Python 2.x.y installed, check http://python.org/ for further help. To exit python type `quit()`. 

### Installation ###

Change into your workspace directory and clone this repo: 
`git clone http://github.com/insika/restful_insika`.

Download `web.py-0.37.tar.gz` from: http://webpy.org/static/ and extract the folder `web` and the files `PKG-INFO` and `setup.py` into the working directory `restful_insika`. 

Change into the working directory: 
`cd restful_insika` 
and install web.py: 
`python setup.py install`.

### Usage ###

Start the server by typing: 
`python restful_insika.py` 
and point your browser to http://localhost:8080/ . 
If you want to use another ip address, specify it: 
`python restful_insika.py <ip_addr>`.


### Licence ###

restful_insika is release under the GNU General Public License version 2. See `gpl-2.0.txt` for details.

