################################################################################
##                                                                            ##
## This file is a part of TADEK.                                              ##
##                                                                            ##
## TADEK - Test Automation in a Distributed Environment                       ##
## (http://tadek.comarch.com)                                                 ##
##                                                                            ##
## Copyright (C) 2011 Comarch S.A.                                            ##
## All rights reserved.                                                       ##
##                                                                            ##
## TADEK is free software for non-commercial purposes. For commercial ones    ##
## we offer a commercial license. Please check http://tadek.comarch.com for   ##
## details or write to tadek-licenses@comarch.com                             ##
##                                                                            ##
## You can redistribute it and/or modify it under the terms of the            ##
## GNU General Public License as published by the Free Software Foundation,   ##
## either version 3 of the License, or (at your option) any later version.    ##
##                                                                            ##
## TADEK is distributed in the hope that it will be useful,                   ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of             ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the              ##
## GNU General Public License for more details.                               ##
##                                                                            ##
## You should have received a copy of the GNU General Public License          ##
## along with TADEK bundled with this file in the file LICENSE.               ##
## If not, see http://www.gnu.org/licenses/.                                  ##
##                                                                            ##
## Please notice that Contributor Agreement applies to any contribution       ##
## you make to TADEK. The Agreement must be completed, signed and sent        ##
## to Comarch before any contribution is made. You should have received       ##
## a copy of Contribution Agreement along with TADEK bundled with this file   ##
## in the file CONTRIBUTION_AGREEMENT.pdf or see http://tadek.comarch.com     ##
## or write to tadek-licenses@comarch.com                                     ##
##                                                                            ##
################################################################################

from tadek.core import log
from tadek.core import location
from tadek.engine import channels
from tadek.engine import testresult
from tadek.engine.loader import TestLoader
from tadek.engine.runner import TestRunner
from tadek.engine.channels.summarychannel import COUNTER_CORE_DUMPS, \
                            COUNTER_N_TESTS, COUNTER_TESTS_RUN, COUNTER_RUN_TIME
from tadek.engine.testexec import STATUS_NO_RUN, STATUS_NOT_COMPLETED, \
                            STATUS_PASSED, STATUS_FAILED, STATUS_ERROR

from utils import exitWithStatus, printSeparator

#: Name of a summary channel
SUMMARY_CHANNEL = "_summary"

def runTestCases(tests, locations, devices):
    '''
    A function responsible for running the given test cases.
    '''
    log.debug("Run test cases from '%s' locations using '%s' devices: %s"
               % (", ".join(locations), ", ".join([str(d) for d in devices]),
                  ", ".join(tests)))
    loader = TestLoader()
    amountToRun = 0
    for path in locations:
        location.add(path)
    if not isinstance(tests, (list, tuple)):
        tests = [tests]
    suites, errors = loader.loadFromNames(*tests)

    ncases = 0
    for test in suites:
        ncases += test.count()
    print (" LOADED %d TEST CASES " % ncases).center(80, '-') + '\n'

    if len(errors) > 0:
        print "There were errors during loading test cases:"
        for error in errors:
            print "%s\n%s" % (error.name, error.traceback)
            printSeparator()
        print

    if not ncases:
        #Nothing to do
        exitWithStatus(status=0)

    log.info("Start running tests: %s" % suites)
    channels.add("SummaryChannel", SUMMARY_CHANNEL)
    result = testresult.TestResult()
    runner = TestRunner(devices, suites, result)

    for device in devices:
        device.connect()
    try:
        runner.start()
        runner.join()
    except KeyboardInterrupt:
        runner.stop()
    finally:
        for device in devices:
            if device.isConnected():
                device.disconnect()
    return result

def printResult(result):
    '''
    Prints the given test result.
    '''
    log.debug("Print test result: %s" % result)
    summary = result.get(name=SUMMARY_CHANNEL)[0].getSummary()
    log.info("Print summary of test execution results: %s" % summary)
    report = "Ran %d of %d test cases in %s" % (summary[COUNTER_TESTS_RUN],
                                                summary[COUNTER_N_TESTS],
                                                summary[COUNTER_RUN_TIME])
    print '\n', report
    printSeparator(len(report))
    if summary[STATUS_PASSED]:
        print "Tests passed:\t\t%d" % summary[STATUS_PASSED]
    if summary[STATUS_FAILED]:
        print "Tests failed:\t\t%d" % summary[STATUS_FAILED]
    if summary[STATUS_NOT_COMPLETED]:
        print "Tests not completed:\t%d" % summary[STATUS_NOT_COMPLETED]
    if summary[COUNTER_CORE_DUMPS]:
        print "Core dumps:\t\t%d" % summary[COUNTER_CORE_DUMPS]
    if summary[STATUS_ERROR]:
        print "Tests error:\t\t%d" % summary[STATUS_ERROR]
    filechls = [chl for chl in result.get(cls=channels.TestResultFileChannel)
                    if chl.isActive()]
    if filechls:
        print "Result file:" if len(filechls) == 1 else "Result files:"
        for channel in filechls:
            print "\t%s" % channel.filePath()
    printSeparator()

    status = (1 if (summary[STATUS_FAILED] + summary[STATUS_ERROR] +
                    summary[STATUS_NOT_COMPLETED]) else 0)
    exitWithStatus("FAILURE" if status else "SUCCESS", status)

