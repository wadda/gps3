# README #

gps3 is a python3 interface for gpsd.

gpsd (http://www.catb.org/gpsd/) is a fabulous application that deserves a Python3 interface.

The goal is to deliver a package to the Cheese Shop (https://pypi.python.org/pypi/gps3/0.1a1) that equals the quality of the source and craftsmanship behind it.

It is a match made in heaven.
![gps3api-mod.dia.png](https://bitbucket.org/repo/nGqxd8/images/2994450553-gps3api-mod.dia.png)
### How do I get set up? ###

* Summary of set up
The gpsd source can be found at http://download.savannah.gnu.org/releases/gpsd/

If you're hardcore you can build it by following the instructions.  It uses scons and such.  If you gather your tools, it should not be a problem.  [All the installation info](http://www.catb.org/gpsd/installation.html) is here: http://www.catb.org/gpsd/installation.html

If you're like most of humanity **sudo apt-get install gpsd python-gps**

This gives you the daemon, library, and the python fun-pack.  If you use a different package system you are obviously smart enough to figure out how to make yours go.

* Configuration

Setup of the gpsd is straight forward.  Autostart is your choice.  We tend to flag *-n -b -G* in /etc/default/gpsd, to cut down on problems with a spectrum of gps devices and applications.  Default setting the rest of the way.  Generally, there are no surprises.

```
#!bash

usage: gpsd [-b] [-n] [-N] [-D n] [-F sockfile] [-G] [-P pidfile] [-S port] [-h] device...
  Options include:
  -b		     	    = bluetooth-safe: open data sources read-only
  -n			    = don't wait for client connects to poll GPS
  -N			    = don't go into background
  -F sockfile		    = specify control socket location
  -G         		    = make gpsd listen on INADDR_ANY
  -P pidfile	      	    = set file to record process ID
  -D integer (default 0)    = set debug level
  -S integer (default 2947) = set port for daemon
  -h		     	    = help message
  -V			    = emit version and exit.
A device may be a local serial device for GPS input, or a URL of the form:
     {dgpsip|ntrip}://[user:passwd@]host[:port][/stream]
     gpsd://host[:port][/device][?protocol]
in which case it specifies an input source for GPSD, DGPS or ntrip data.

```