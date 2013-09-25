#-*- coding: utf8 -*-
import re
import os
from shutil import copyfile
from stat import S_ISDIR

__all__ = [
    "AntPatternDirectoryScanner",
    "DEFAULTEXCLUDES"
]

DEFAULTEXCLUDES = [
    "**/*~",
    "**/#*#",
    "**/.#*",
    "**/%*%",
    "**/._*",
    "**/CVS",
    "**/CVS/**",
    "**/.cvsignore",
    "**/SCCS",
    "**/SCCS/**",
    "**/vssver.scc",
    "**/.svn",
    "**/.svn/**",
    "**/.DS_Store",
    "**/.git",
    "**/.git/**",
    "**/.gitattributes",
    "**/.gitignore",
    "**/.gitmodules",
    "**/.hg",
    "**/.hg/**",
    "**/.hgignore",
    "**/.hgsub",
    "**/.hgsubstate",
    "**/.hgtags",
    "**/.bzr",
    "**/.bzr/**",
    "**/.bzrignore"
]


def glob2regexp(glob: str) -> str:
    """Translates glob pattern into regexp string.
    """
    res = ""
    escaping = False
    incurlies = 0
    pc = None  # Previous char
    for cc in glob.strip():
        if cc == "*":
            res += ("\\*" if escaping else ".*")
            escaping = False
        elif cc == "?":
            res += ("\\?" if escaping else ".")
            escaping = False
        elif cc in [".", "(", ")", "+", "|", "^", "$", "@", "%"]:
            res += "\\"
            res += cc
            escaping = False
        elif cc == "\\":
            if escaping:
                res += "\\\\"
                escaping = False
            else:
                escaping = True
        elif cc == "{":
            if escaping:
                res += "\\{"
            else:
                res += "("
                incurlies += 1
            escaping = False
        elif cc == "}":
            if incurlies > 0 and not escaping:
                res += ")"
                incurlies -= 1
            elif escaping:
                res += "\\}"
            else:
                res += "}"
            escaping = False
        elif cc == ",":
            if incurlies > 0 and not escaping:
                res += "|"
            else:
                res += cc
            escaping = False
        else:
            if not escaping and cc.isspace():
                if pc.isspace():
                    res += "\\s*"
            else:
                res += cc
            escaping = False
        pc = cc
    return res


class AntPatternMatcher(object):
    def __init__(self, includes=None, excludes=None):
        if type(includes) is str:
            includes = [includes]
        if type(excludes) is str:
            excludes = [excludes]
        self._excludes = [self.normpattern(e).split('/')
                          for e in (excludes if excludes is not None else [])]
        self._includes = [self.normpattern(e).split('/')
                          for e in (includes if includes is not None else ["**"])]

    def normpattern(self, pattern):
        if len(pattern) == 0 or pattern.isspace():
            return "**"
        pattern = pattern.replace("\\", "/").strip("/").split("/")
        npattern = []
        inmd = False  # If True we are in **/pattern
        for pitem in pattern:
            if pitem == "**":
                if inmd is True:
                    continue
                inmd = True
            elif pitem == "*" and inmd:
                continue
            else:
                pitem = glob2regexp(pitem)
                inmd = False
            npattern.append(pitem)
        return '/'.join(npattern)

    def vote(self, val, match, prefixonly=False):
        if type(val) is str:
            val = val.split("/")
        if type(match) is str:
            match = match.split("/")
        if type(val) is not list:
            raise ValueError("`val` should be a string or iterable")
        if type(match) is not list:
            raise ValueError("`match` should be a string or iterable")

        mind = 0
        expectnext = None
        expectnextind = None
        travesedmatches = set()

        for el in val:
            if mind >= len(match):
                return False

            mv = match[mind]
            if mv == "**":
                if expectnext is None and len(match) > mind + 1:
                    expectnext = match[mind + 1]
                    expectnextind = mind + 1

            if not self.match(el, mv):
                return False

            travesedmatches.add(mind)
            if expectnext is not None:
                if self.match(el, expectnext):
                    travesedmatches.add(expectnextind)
                    expectnext = None
                    expectnextind = None
                    mind += 2
            else:
                if mv != "**":
                    mind += 1

        if not prefixonly:
            for i in range(mind, len(match)):
                if match[i] != "**" and i not in travesedmatches:
                    return False
        return True

    def match(self, val, pattern):
        if pattern == "**":
            pattern = ".*"
        return re.match(pattern, val, re.I)

    def voteAll(self, val, prefixonly=False):
        if not prefixonly:
            for e in self._excludes:
                if self.vote(val, e):
                    return False
        for e in self._includes:
            if self.vote(val, e, prefixonly):
                return True
        return False


class AntPatternDirectoryScanner(object):
    def __init__(self, rootdir, includes="**", excludes=None, verbose=False):
        """Constructs a directory scanner with specified include/exclude ant-like matching patterns.
        Exclude patterns have precedence over includes.

        >>> ds = AntPatternDirectoryScanner("foo/bar", "**/data/**/*.txt")
        ... for filename in ds.scan():
        ...    print(filename)
        ...

        :param rootdir: Base directory for pattern matching
        :param includes: Include ant path patterns (`list` or `str' for single pattern). Default: `**`.
        :param excludes: Exclude ant path patterns (`list` or `str' for single pattern). Default: `None`.
        :param verbose: If True debugging messages will be printed during `copy` operation.
        """
        self._rootdir = rootdir
        self._includes = includes
        self._excludes = excludes
        self._verbose = verbose

    def _traverse(self, tdir, acceptfn, ctx=None, inodes=None):
        if inodes is None:
            inodes = set()
        try:
            dlist = os.listdir(tdir)
            dlist.sort()
        except PermissionError as e:
            print("Directory scanning error: ", e)
            return

        for e in dlist:
            epath = os.path.join(tdir, e)
            try:
                stat = os.lstat(epath)
            except OSError as e:
                print("Directory scanning error: ", e)
                continue
            ino = stat.st_ino
            accepted = acceptfn(epath, stat, ctx)
            if accepted and not S_ISDIR(stat.st_mode):
                yield epath
            if accepted is True \
                and S_ISDIR(stat.st_mode) \
                and (ino == 0 or (ino not in inodes)):
                inodes.add(ino)
                yield from self._traverse(epath, acceptfn, ctx, inodes)

    def scan(self, includes=None, excludes=None):
        """Generator of file names matched specified include/exclude ant patterns.
        :rtype : generator
        :param includes: Optional `includes` ant pattern it override pattern specified in constructor.
        :param excludes: Optional `excludes` ant pattern it override pattern specified in constructor.
        >>> ds = AntPatternDirectoryScanner("some/root/path")
        ... for fname in ds.scan(includes=["foo/**/*.txt"])
        ...     print(fname)
        ...
        ... #Equivalent of previous:
        ... ds = AntPatternDirectoryScanner("some/root/path", "foo/**/*.txt")
        ... for fname in ds.scan():
        ...     print(fname)
        """
        matcher = AntPatternMatcher(includes if includes is not None else self._includes,
                                    excludes if excludes is not None else self._excludes)

        def _acceptor(epath, stat, ctx):
            if epath.find(self._rootdir) != 0:
                return False
            parr = epath[len(self._rootdir) + 1:].split(os.sep)
            if matcher.voteAll(parr):
                return True
            elif S_ISDIR(stat.st_mode):
                return matcher.voteAll(parr, True)
            return False

        yield from self._traverse(self._rootdir, _acceptor)

    def copy(self, targetroot):
        """Copies matched and outdated files into another `targetroot` directory.
        Missing directories will be automatically created.
        >>> ds = AntPatternDirectoryScanner("some/dir/**")
        ... ds.copy("target/dir")
        """
        for cf in self.scan():
            of = os.path.join(targetroot, cf[len(self._rootdir) + 1:])
            copy = False
            try:
                if not os.path.exists(of) or \
                                os.lstat(cf).st_mtime > os.lstat(of).st_mtime:
                    copy = True
            except FileNotFoundError:
                copy = True
            if copy:
                if self._verbose:
                    print("{} Copying file {} => {}".format(self, cf, of))
                os.makedirs(os.path.dirname(of), exist_ok=True)
                copyfile(cf, of)

    def __str__(self):
        return "<AntPatternDirectoryScanner: includes={} excludes={}>".format(self._includes, self._excludes)

