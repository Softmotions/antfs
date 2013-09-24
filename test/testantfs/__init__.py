import unittest
import os
from antfs import AntPatternMatcher, AntPatternDirectoryScanner


class TestAntfs(unittest.TestCase):
    def assertStrContains(self, stack, substr):
        self.assertTrue(str(stack).find(str(substr)) >= 0)

    def testAntFs1(self):
        am = AntPatternMatcher()
        self.assertEqual(am.normpattern(""), "**")
        self.assertEqual(am.normpattern("/**/test/**/test2/*/*/file*.txt"), "**/test/**/test2/.*/.*/file.*\\.txt")
        self.assertEqual(am.normpattern("/**/**/test/**/test2/*/*/file*.txt"), "**/test/**/test2/.*/.*/file.*\\.txt")
        self.assertEqual(am.normpattern("/**/**/test/**/test2/*/**/*/file*.txt"), "**/test/**/test2/.*/**/file.*\\.txt")

        self.assertTrue(am.vote(["data"], am.normpattern("**/data/**").split("/")))
        self.assertTrue(am.vote(["a", "b", "c"], am.normpattern("a/*/c*").split("/")))
        self.assertFalse(am.vote(["a", "b", "c"], am.normpattern("a/*/d").split("/")))
        self.assertTrue(am.vote(["a", "b", "c"], am.normpattern("**").split("/")))
        self.assertTrue(am.vote(["a", "b", "c"], am.normpattern("**/**").split("/")))
        self.assertTrue(am.vote(["a", "b", "c"], am.normpattern("*/*/*").split("/")))
        self.assertFalse(am.vote(["a", "b", "c"], am.normpattern("*/*/*/*").split("/")))
        self.assertFalse(am.vote(["a", "b", "c"], am.normpattern("*/*/*/f").split("/")))
        self.assertFalse(am.vote(["a", "b", "c"], am.normpattern("*").split("/")))
        self.assertFalse(am.vote(["a", "b", "c"], am.normpattern("*/*").split("/")))
        self.assertTrue(am.vote(["a", "b", "c"], am.normpattern("a/**/c").split("/")))
        self.assertTrue(am.vote(["a", "b", "c"], am.normpattern("a/**/*").split("/")))
        self.assertTrue(am.vote(["a", "b", "c", "d", "e"], am.normpattern("a/b/c/d/e").split("/")))
        self.assertTrue(am.vote(["a", "b", "c", "d", "e"], am.normpattern("a/**/e").split("/")))
        self.assertTrue(am.vote(["a", "b", "c", "d", "e"], am.normpattern("a/**/d/e").split("/")))
        self.assertTrue(am.vote(["a", "b", "c", "d", "e"], am.normpattern("a/**/c/d/e").split("/")))
        self.assertFalse(am.vote(["a", "b", "c", "d", "e"], am.normpattern("a/**/c/d/f").split("/")))
        self.assertFalse(am.vote(["a", "b", "c", "d", "e"], am.normpattern("a/**/f/d/e").split("/")))
        self.assertTrue(am.vote(["a", "b", "c", "d", "e", "f", "g"], am.normpattern("a/**/d/**/g").split("/")))
        self.assertTrue(am.vote(["a", "b", "c", "d"], am.normpattern("**/*").split("/")))
        self.assertTrue(am.vote(["a", "b", "c", "d"], am.normpattern("a/**/*").split("/")))
        self.assertTrue(am.vote(["src", "p1", "index.cpp"], am.normpattern("src/**/*.cpp").split("/")))
        self.assertTrue(am.vote(["src", "p1", "p2", "index.cpp"], am.normpattern("src/**/*.cpp").split("/")))
        self.assertTrue(am.vote(["src", "index.cpp"], am.normpattern("src/**/*.cpp").split("/")))
        self.assertTrue(am.vote(["src", "index.cpp"], am.normpattern("src/*.cpp").split("/")))
        self.assertFalse(am.vote(["src", "p1", "index.cpp"], am.normpattern("src/*.cpp").split("/")))
        self.assertTrue(am.vote(["src", "p1", "index.cpp"], am.normpattern("src/*/*.cpp").split("/")))
        self.assertTrue(am.vote(["src", "p1", "index.cpp"], am.normpattern("src/*/*.{cpp}").split("/")))
        self.assertTrue(am.vote(["src", "p1", "index.cpp"], am.normpattern("src/*/*.{cpp,java}").split("/")))
        self.assertTrue(am.vote(["src", "p1", "index.java"], am.normpattern("src/*/*.{cpp,java}").split("/")))
        self.assertTrue(am.vote("uis/dist/uisclient/.svn/props".split("/"),
                                am.normpattern("**/.svn/**").split("/")))
        self.assertTrue(am.vote("data/layout/asm5.jn".split("/"),
                                am.normpattern("**/dat?/**/*")))
        self.assertFalse(am.vote("data/layout/asm5.jn".split("/"),
                                 am.normpattern("**/data2/**/*")))

    def testAntFs2(self):
        root = os.path.dirname(__file__)
        ds = AntPatternDirectoryScanner(root)
        res = []

        for e in ds.scan("**/data/**"):
            res.append(e[len(root) + 1:])
        self.assertEqual(len(res), 5)
        self.assertTrue("data/a/abc.txt" in res)
        self.assertTrue("data/b/c/efg.txt" in res)
        self.assertTrue("data/b/c.txt" in res)
        self.assertTrue("data/b/b.txt" in res)
        self.assertTrue("data/a/b.cpp" in res)

        res = []
        for e in ds.scan("**/data/**/*.txt"):
            res.append(e[len(root) + 1:])
        self.assertEqual(len(res), 4)
        self.assertFalse("data/a/b.cpp" in res)

        res = []
        for e in ds.scan("**/data/a/*{.txt,.cpp}"):
            res.append(e[len(root) + 1:])
        self.assertEqual(len(res), 2)
        self.assertTrue("data/a/b.cpp" in res)
        self.assertTrue("data/a/abc.txt" in res)

