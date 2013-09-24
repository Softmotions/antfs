antfs: Python3 `Ant <http://ant.apache.org/manual/dirtasks.html#patterns>`_ path matching library
===================================================================

============
Usage:
============

Select file paths matched the specified `ant path pattern <http://ant.apache.org/manual/dirtasks.html#patterns>`_ :

>>> ds = AntPatternDirectoryScanner("foo/bar", "foo/**/*.txt")
... for filename in ds.scan():
...    print(filename)
...


Copy matched files into target directory:

>>> ds = AntPatternDirectoryScanner("some/dir/**")
... ds.copy("target/dir")