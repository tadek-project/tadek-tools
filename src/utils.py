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

import sys
import optparse
import textwrap

from tadek.core import log
from tadek.core import devices
from tadek.connection.device import Device

def getDevices(deviceArgs):
    '''
    Converts command-line arguments representing devices.

    :param deviceArgs: Devices identifiers
    :type deviceArgs: list [string]
    :return: List of devices
    :rtype: list [tadek.connection.device.Device]
    '''
    log.debug("Get devices from command-line arguments: %s" % deviceArgs)
    deviceList = []
    if deviceArgs is None or deviceArgs == [None]:
        log.info("Using default device %s:%d"
                 % (devices.DEFAULT_IP, devices.DEFAULT_PORT) )
        deviceList.append(Device('localhost', devices.DEFAULT_IP,
                                 devices.DEFAULT_PORT))
    else:
        for arg in deviceArgs:
            device = devices.get(arg)
            if device is None:
                address = arg.split(':')
                if len(address) == 2:
                    address, port = address
                    port = int(port)
                elif len(address) == 1:
                    address, port = address[0], devices.DEFAULT_PORT
                else:
                    exitWithError("Invalid format of a device: %s" % arg)
                device = Device(address + ':' + str(port), address, port)
            log.info("Adding a device: %s=%s:%d"
                      % (device.name, device.address[0], device.address[1]))
            deviceList.append(device)
    return deviceList

def exitWithStatus(message=None, status=0):
    '''
    Logs and prints the given message and exits with the specified status code.
    '''
    if message:
        log.info(message)
        print message
    else:
        log.info("Exit with status: %d" % status)
    sys.exit(status)

def exitWithError(error):
    '''
    Logs error, prints it and exits the program with 2 code.

    :param error: An error message
    :type error: string
    '''
    log.info(error)
    print >> sys.stderr, error
    sys.exit(2)

def printSeparator(length=80):
    '''
    Prints a separator line of the given length.
    '''
    print length * '-'

class LineFormatter(optparse.IndentedHelpFormatter):
    '''
    A class for formatting tools help messages.
    '''
    def format_description(self, description):
        '''
        Creates tool description in the help section.

        :return: Well formatted, human-readable tool description
        :rtype: string
        '''
        if description:
            width = self.width - self.current_indent
            indent = ' '*self.current_indent
            parts = description.strip('\n').split('\n')
            formatted = []
            for part in parts:
                formatted.append(textwrap.fill(part, width,
                                               initial_indent=indent,
                                               subsequent_indent=indent))
            return '\n'.join(formatted) + '\n'
        else:
            return ''

