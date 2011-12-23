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

import os

from tadek.core import log
from tadek.core import constants
from tadek.core import accessible
from tadek.core import utils

from utils import exitWithStatus, exitWithError, printSeparator

__all__ = ["performRequest"]

def _printInlineAttr(accessible, attr, name=None):
    '''
    Prints a value of the given accessible attribute in-line.
    '''
    if not name:
        name = attr
    value = getattr(accessible, attr)
    if value is None:
        return False
    print "%s: %s" % (name.upper(), value)
    return True

def _printListAttr(accessible, attr, name=None):
    '''
    Prints values of the given list accessible attribute.
    '''
    if not name:
        name = attr
    value = getattr(accessible, attr)
    if not value:
        return False
    print "%s:\n\t%s" % (name.upper(), "\n\t".join(value))
    return True

def _printDictAttr(accessible, attr, name=None):
    '''
    Prints values of the given dictionary accessible attribute.
    '''
    if not name:
        name = attr
    value = getattr(accessible, attr)
    if not value:
        return False
    print "%s:" % name.upper()
    for key, val in value.iteritems():
        print "\t%s: %s" % (key, val)
    return True

def _printTextAttr(accessible, *args):
    '''
    Prints text of the given accessible.
    '''
    if accessible.text is None:
        return False
    editable = " (editable)" if accessible.editable else ''
    print "TEXT%s:\n%s" % (editable, accessible.text)
    return True

def _printRelationsAttr(accessible, *args):
    '''
    Prints relations of the given accessible.
    '''
    if not accessible.relations:
        return False
    print "RELATIONS:"
    for relation in accessible.relations:
        print "\t%s: %s"% (relation.type, ", ".join([str(t) for t in relation]))
    return True

# A column separator in the accessible tree
_COLUMN_SEPARATOR = '|'

# A list of basic accessible attributes
_ATTRS_BASIC = (
    ("path", _printInlineAttr),
    ("name", _printInlineAttr),
    ("role", _printInlineAttr),
    ("count", _printInlineAttr, "children"),
)

# A list of extra accessible attributes
_ATTRS_EXTRA = (
    ("description", _printInlineAttr),
    ("position", _printInlineAttr),
    ("size", _printInlineAttr),
    ("attributes", _printDictAttr),
    ("actions", _printListAttr),
    ("text", _printTextAttr),
    ("value", _printInlineAttr),
    ("states", _printListAttr),
    ("relations", _printRelationsAttr),
)

def printAccessibleDetails(accessible, attribute):
    '''
    Prints details about the given accessible.
    '''
    log.debug("Print details about accessible: %s" % accessible)
    printSeparator()
    for attr in _ATTRS_BASIC:
        name, func = attr[:2]
        func(accessible, name, *attr[2:])
    print
    for attr in _ATTRS_EXTRA:
        name, func = attr[:2]
        if name != attribute and attribute != "all":
            continue
        if not func(accessible, name, *attr[2:]) and name == attribute:
            print "Element has no %s" % name

def _countColumnLens(accessible, lens):
    '''
    Counts length of each of column displaying a basic attibute of accessibles. 
    '''
    for i, attr in enumerate(_ATTRS_BASIC):
        item = getattr(accessible, attr[0])
        if not item:
            continue
        if not isinstance(item, basestring):
            item = str(item)
        lens[i] = max(len(item), lens[i])
    for child in accessible.children(force=False):
        _countColumnLens(child, lens)

def _printAccessibleAligned(accessible, lens):
    '''
    Aligns and prints the given accessible recursively.
    '''
    row = []
    for i, attr in enumerate(_ATTRS_BASIC):
        item = getattr(accessible, attr[0])
        if item is None:
            item = ''
        if not isinstance(item, basestring):
            item = str(item)
        row.append(utils.encode(item).ljust(lens[i]))
    print _COLUMN_SEPARATOR.join(row)
    for child in accessible.children(force=False):
        _printAccessibleAligned(child, lens)

def printAccessibleTree(accessible):
    '''
    Prints the given accessible tree recursively.
    '''
    log.debug("Print accessible tree: %s" % accessible)
    lens = [len(attr[2 if len(attr) > 2 else 0]) for attr in _ATTRS_BASIC]
    _countColumnLens(accessible, lens)
    # Print column header
    row = []
    for i, attr in enumerate(_ATTRS_BASIC):
        name = attr[2 if len(attr) > 2 else 0]
        row.append(name.upper().center(lens[i]))
    length = (sum(lens) + len(lens) - 1)
    printSeparator(length)
    print _COLUMN_SEPARATOR.join(row)
    printSeparator(length)
    # Print accessible tree
    log.info("Print accessible tree using column lengths: %s"
              % ", ".join([str(i) for i in lens]))
    _printAccessibleAligned(accessible, lens)

def performRequest(device, options):
    '''
    Performs a request on the given device using the specified options.

    :param device: A device to perform the request on
    :type device: tadek.connection.device.Device
    :param options: Options representing the request
    :type params: dictionary
    '''
    log.debug("Perform a request on '%s' device using options: %s"
               % (device, options))
    path = accessible.Path(*options.pop("path").split('/')[1:])
    device.connect()
    try:
        if "action" in options:
            status = device.doAccessible(path, options["action"])
        elif "set-text" in options:
            text = options["set-text"]
            status = device.setAccessible(path, text=text)
        elif "set-text-file" in options:
            fn = options["set-text-file"]
            if not os.path.isfile(fn):
                exitWithError("There is no such file: %s" % fn)
            fd = None
            try:
                fd = open(fn)
                text = fd.read()
            finally:
                if fd:
                    fd.close()
            status = device.setAccessible(path, text=text)
        elif "set-value" in options:
            value = float(options["set-value"])
            status = device.setAccessible(path, value=value)
        elif "mouse-click" in options:
            x, y = options["mouse-click"]
            button = options["button"]
            status = device.mouseEvent(path, int(x), int(y), button, "CLICK")
        elif "mouse-double-click" in options:
            x, y = options["mouse-double-click"]
            button = options["button"]
            status = device.mouseEvent(path, int(x), int(y),
                                       button, "DOUBLE_CLICK")
        elif "mouse-press" in options:
            x, y = options["mouse-press"]
            button = options["button"]
            status = device.mouseEvent(path, int(x), int(y), button, "PRESS")
        elif "mouse-release" in options:
            x, y = options["mouse-release"]
            button = options["button"]
            status = device.mouseEvent(path, int(x), int(y), button, "RELEASE")
        elif "mouse-absolute-motion" in options:
            x, y = options["mouse-absolute-motion"]
            status = device.mouseEvent(path, int(x), int(y),
                                       '', "ABSOLUTE_MOTION")
        elif "mouse-relative-motion" in options:
            x, y = options["mouse-relative-motion"]
            status = device.mouseEvent(path, int(x), int(y),
                                       '', "RELATIVE_MOTION")
        elif "key" in options:
            key = options["key"].upper()
            if key in constants.KEY_SYMS:
                key = constants.KEY_SYMS[key]
            elif len(key) == 1:
                key = ord(key)
            elif key.startswith("0X"):
                key = int(key, 16)
            else:
                key = int(key)
            if "modifiers" in options:
                modifiers = [constants.KEY_CODES[mod]
                                    for mod in options["modifiers"]]
            else:
                modifiers = []
            status = device.keyboardEvent(path, key, modifiers)
        elif "dump" in options or "dump-all" in options:
            all = False
            if "dump" in options:
                depth = int(options["dump"])
            else:
                depth = -1
            if "output" in options:
                fn = options["output"]
                all = True
            obj = device.getAccessible(path, depth, all=all)
            if obj is None:
                exitWithStatus("There is no such path: %s" % path, 1)
            if all:
                printSeparator()
                utils.saveXml(obj.marshal(), fn)
                exitWithStatus("Dump saved to file: %s" % fn)
            else:
                printAccessibleTree(obj)
                exitWithStatus()
        else:
            for name in (["all"] + [attr[0] for attr in _ATTRS_EXTRA]):
                if name in options:
                    break
            else:
                exitWithError("Invalid request options: %s" % options)
            obj = device.getAccessible(path, 0, **{name: True})
            if obj is None:
                exitWithStatus("There is no such path: %s" % path, 1)
            printAccessibleDetails(obj, name)
            exitWithStatus()
    finally:
        if device.isConnected():
            device.disconnect()
    printSeparator()
    if status:
        exitWithStatus("SUCCESS")
    else:
        exitWithStatus("FAILURE", 1)

