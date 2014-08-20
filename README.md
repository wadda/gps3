# README #

This README would normally document whatever steps are necessary to get your application up and running.

...but it's not.

### What is this repository for? ###
gps3 is a python3 interface for gpsd.

gpsd (http://www.catb.org/gpsd/) is a fabulous application that deserves a Python3 interface.

The goal is to deliver a package to the Cheese Shop (https://pypi.python.org/pypi/gps3/0.1a1)

It is a match made in heaven.
![gps3api.png](https://bitbucket.org/repo/nGqxd8/images/2743857718-gps3api.png)

### How do I get set up? ###

* Summary of set up
The gpsd source can be found at http://download.savannah.gnu.org/releases/gpsd/

If you're hardcore you can build it by following the instructions.  It uses scons and such.  If you gather your tools, it should not be a problem.

If you're like most of humanity **sudo apt-get install gpsd python-gps**

This gives you the daemon, libgps, and python fun-pack.  If you use a different package system you are obviously smart enough to figure it out.

* Configuration
Setup of the gpsd is straight forward.  We tend to flip *-n -b -G* flags to cut down on problems, with default setting the rest of the way.  Sometime *-N* is for non-daemon execution and *-D* for diagnostic integer up to *9*, depending how much you want to read. 


* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact
