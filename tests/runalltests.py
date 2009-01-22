#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Run all test modules in current directory.
"""

import unittest
import glob
import logging
from StringIO import StringIO

import fms
from fms.utils import YamlParamsParser, close_files

def sourceList():
    """
    Return list of all python modules except this one in current dir
    """
    liste = []
    for s in glob.glob("*.py"):
        if s == 'runalltests.py':
            continue
        s = s.split('.')[0]
        liste.append(s)
    return liste

def expList():
    """
    Return list of experiments conffiles in fixtures/fulltest dir
    """
    return glob.glob("fixtures/fulltests/*.yml")


logger = fms.set_logger('info','fms-tests')

logger.info("Running unittests")
suite = unittest.TestSuite()
for modtestname in sourceList():
    exec "import %s" % modtestname
    modtest = globals()[modtestname]
    if hasattr(modtest, 'suite'):
        suite.addTest(modtest.suite())
    else:
        suite.addTest(unittest.defaultTestLoader.loadTestsFromModule(modtest))
tests = unittest.TestSuite(suite)
unittest.TextTestRunner(verbosity=2).run(tests)

for simconffile in expList():
    logger.info("Running %s" % simconffile)
    params = YamlParamsParser(simconffile)
    close_files(params)
    params.outputfile = StringIO()
    world = fms.set_world(params)
    engineslist = fms.set_engines(params)
    agentslist = fms.set_agents(params)
    for e in engineslist:
        e['instance'].run(world, agentslist, e['market']['instance'])
    benchfile = "%s.csv" % simconffile.split('.')[0]
    benchmark = open(benchfile).read()
    testresult = params.outputfile.getvalue()
    if not benchmark == testresult:
        logger.error("%s failed" % simconffile)
        print testresult
    logger.info("%s done." % simconffile)
            

