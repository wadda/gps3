# README #

gps3 is a python3 interface for gpsd.

gpsd (http://www.catb.org/gpsd/) is a fabulous application that deserves a Python3 interface.

The goal is to deliver a package to the Cheese Shop (https://pypi.python.org/pypi/gps3/0.1a1) that equals the quality of the source and craftmanship of the people behind it.

It is a match made in heaven.
![gps3api-mod.png](https://bitbucket.org/repo/nGqxd8/images/2110656712-gps3api-mod.png)

### How do I get set up? ###

The gpsd source can be found at http://download.savannah.gnu.org/releases/gpsd/

If you're hardcore you can build it by following the instructions.  It uses scons and such.  If you gather your tools, it should not be a problem.  Be very bold and just jump in.

If you're like most of humanity **sudo apt-get install gpsd python-gps**

This gives you the daemon, the library, and the python fun-pack.  If you use a different package system on another POSIX compliant machine, you are obviously smart enough to figure out what need to be done to make it work. I am not.

* Configuration

Setup of the gpsd is straight forward.  Autostart is your choice.  We tend to flag *-n -b -G* to cut down on problems with a range of gps units and applications.  It might be voodoo.  Default settings the rest of the way is a solid choice.  Sometimes *-N* is for non-daemon execution and *-D* for diagnostic integer up to *9*, depending how much you want to read and those also *tend* to be from the command line.