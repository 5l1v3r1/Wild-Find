#!/usr/bin/env python
#
#
# Wild Find
#
#
# Copyright 2014 - 2017 Al Brown
#
# Wildlife tracking and mapping
#
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


from PySide import QtUiTools, QtCore

from wildfind.falconer.utils import get_resource_ui


class UiLoader(QtUiTools.QUiLoader):
    def __init__(self, instance):
        QtUiTools.QUiLoader.__init__(self, instance)
        self._instance = instance

    def createWidget(self, className, parent=None, name=''):
        widget = None
        if parent is None and self._instance:
            widget = self._instance
        elif className in QtUiTools.QUiLoader.availableWidgets(self):
            widget = QtUiTools.QUiLoader.createWidget(self,
                                                      className,
                                                      parent,
                                                      name)
        else:
            if hasattr(self._instance, 'customWidgets'):
                if className in self._instance.customWidgets.keys():
                    widget = self._instance.customWidgets[className](parent)
                else:
                    error = 'Unknown widget \'{}\''.format(className)
                    raise KeyError(error)
            else:
                error = 'Instance does not specify \'customWidgets\''
                raise AttributeError(error)

        if self._instance is not None and widget is not None:
            setattr(self._instance, name, widget)

        return widget


def loadUi(instance, fileName):
    loader = UiLoader(instance)
    uiFile = get_resource_ui(fileName)
    widget = loader.load(uiFile)
    QtCore.QMetaObject.connectSlotsByName(widget)

    return widget

if __name__ == '__main__':
    print 'Please run falconer.py'
    exit(1)
