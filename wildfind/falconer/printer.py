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

from PySide import QtGui, QtCore


def print_report(printer, fileName, widgetSurveys, widgetScans, widgetSignals, widgetMap):
    sizeTitle = 12
    sizeSubtitle = 10
    sizeText = 8

    printer.setPageMargins(12, 16, 12, 20, QtGui.QPrinter.Millimeter)

    document = QtGui.QTextDocument()
    document.setPageSize(QtCore.QSizeF(printer.pageRect().size()))
    cursor = QtGui.QTextCursor(document)

    surveys = widgetSurveys.get()
    scans = widgetScans.get()
    signals = widgetSignals.get()
    mapImage = widgetMap.get_map()

    insert_block(cursor, align=QtCore.Qt.AlignHCenter)
    __set_text_size(cursor, sizeTitle)
    cursor.insertText('Falconer Survey\n')

    insert_block(cursor)
    __set_text_size(cursor, sizeSubtitle)
    cursor.insertText('File name')
    insert_block(cursor, indent=1)
    __set_text_size(cursor, sizeText)
    cursor.insertText(fileName + '\n\n')

    insert_block(cursor)
    __set_text_size(cursor, sizeSubtitle)
    cursor.insertText('Surveys')
    insert_block(cursor, indent=1)
    __set_text_size(cursor, sizeText)
    for survey in surveys:
        cursor.insertText('{}  '.format(survey))
    cursor.insertText('\n\n')

    insert_block(cursor)
    __set_text_size(cursor, sizeSubtitle)
    cursor.insertText('Time range')
    insert_block(cursor, indent=1)
    __set_text_size(cursor, sizeText)
    timeMin = min(scans)
    timeMax = max(scans)
    timeFrom = QtCore.QDateTime().fromTime_t(timeMin).toString()
    timeTo = QtCore.QDateTime().fromTime_t(timeMax).toString()
    if timeMin == timeMax:
        cursor.insertText('{}\n\n'.format(timeFrom))
    else:
        cursor.insertText('{} - {}\n\n'.format(timeFrom, timeTo))

    insert_block(cursor)
    __set_text_size(cursor, sizeSubtitle)
    cursor.insertText('Signals (MHz)')
    insert_block(cursor, indent=1)
    __set_text_size(cursor, sizeText)
    for signal in signals:
        cursor.insertText('{:.4f}  '.format(signal / 1e6))
    cursor.insertText('\n\n')

    pageRect = printer.pageRect()
    height = pageRect.height() - cursor.position()
    width = pageRect.width()
    if width <= height:
        mapImage = mapImage.scaledToWidth(width * 0.8)
    else:
        mapImage = mapImage.scaledToHeight(height * 0.8)
    insert_block(cursor, align=QtCore.Qt.AlignHCenter)
    cursor.insertImage(mapImage)

    document.print_(printer)


def insert_block(cursor, align=None, indent=None):
    block = QtGui.QTextBlockFormat()
    if align is not None:
        block.setAlignment(align)
    if indent is not None:
        block.setIndent(indent)
    cursor.insertBlock(block)


def __set_text_size(cursor, size):
    charFormat = QtGui.QTextCharFormat()
    charFormat.setFontPointSize(size)
    cursor.mergeCharFormat(charFormat)


if __name__ == '__main__':
    print 'Please run falconer.py'
    exit(1)
