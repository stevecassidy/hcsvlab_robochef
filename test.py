from hcsvlab_robochef import utils
import unittest
import os
import subprocess
import sys

from hcsvlab_robochef import monash
from hcsvlab_robochef import cooee
from hcsvlab_robochef import griffith
from hcsvlab_robochef import annotations
from hcsvlab_robochef import ace
from hcsvlab_robochef import braided
from hcsvlab_robochef import utils
from hcsvlab_robochef import metadata
from hcsvlab_robochef import ice
from hcsvlab_robochef import upload
from hcsvlab_robochef import rdf


class BasicTests(unittest.TestCase):
    def testIsAlive(self):
        """trivial test to get us going"""
        self.assert_(True, "panic! how did this happen?")


class AdhocTests(unittest.TestCase):
    def testExpectedFiles(self):
        """
        Test all the example output files we have in the adhoctests directory against the output generated from the last
         run of the ingest program.
        """
        for c in utils.getCorporaArgs(sys.argv):
            res = []
            # utils.listFiles(res, "../systemtests/" + c)
            utils.listFiles(res, '.')
            for f in res:
                if (f.find(
                        ".DS_Store") < 0):  # todo: find a cleaner way to exclude files like the DS_Store (silly macos)
                    result = subprocess.call(["diff", "-w", f, "../output/" + f[
                                                                              14:]])  #need to remove first 14 letters since ../adhoctests is tacked on the front
                    self.assert_((result == 0), (
                    "diff failed for " + f + "\n to see output run diff -w " + f + " ../output/" + f[14:]))

def main():
    suite = unittest.TestSuite()
    suite.addTests([BasicTests("testIsAlive"),
                    monash.unittests(),
                    cooee.unittests(),
                    griffith.unittests(),
                    ice.unittests(),
                    utils.unittests(),
                    annotations.unittests(),
                    ace.unittests(),
                    braided.unittests(),
                    metadata.unittests(),
                    # upload.unittests(), TODO: The upload facilities could possibly be removed for HCSvLab
                    rdf.unittests()])
    unittest.TextTestRunner(verbosity=2).run(suite)


def current():
    suite = unittest.TestSuite()
    suite.addTests([BasicTests("testIsAlive"), monash.unittests()])
    unittest.TextTestRunner(verbosity=2).run(suite)


def adhoc():
    suite = unittest.TestSuite()
    suite.addTests([AdhocTests("testExpectedFiles")])
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == "__main__":
    main()
    # adhoc()
