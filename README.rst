antfs: Python3 `Ant <http://ant.apache.org/manual/dirtasks.html>`_ path matching library
========================================================================================

============
Usage:
============

Select file paths matched the specified `ant path pattern <http://ant.apache.org/manual/dirtasks.html>`_ :

>>> ds = AntPatternDirectoryScanner("foo/bar", "foo/**/*.txt")
... for filename in ds.scan():
...    print(filename)
...


Copy matched files into target directory:

>>> ds = AntPatternDirectoryScanner("some/dir/**")
... ds.copy("target/dir")

==============
Installation:
==============

**************************
(A): Installation with pip
**************************

:: 
  
  umask 022
  sudo pip3 install antfs

  # Upgrading:
  sudo pip3 install antfs --upgrade

*******************************
(B): Installation from sources
*******************************


::
    
    umask 022
    git clone https://github.com/Softmotions/antfs.git
    cd ./antfs
    sudo python3 ./setup.py install
