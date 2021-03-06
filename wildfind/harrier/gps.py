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

import threading
import time

import serial
from serial.serialutil import SerialException

from wildfind.harrier import events

TIMEOUT = 15


class Gps(threading.Thread):
    def __init__(self, gps, queue):
        threading.Thread.__init__(self)
        self.name = 'GPS'

        self._gps = gps
        self._queue = queue

        self._comm = None
        self._timeout = None
        self._cancel = False

        self._sats = {}

        self.start()

    def __timeout(self):
        self.stop()
        events.Post(self._queue).gps_error('GPS timed out')

    def __serial_read(self):
        isSentence = False
        sentence = ''
        while not self._cancel:
            data = self._comm.read(1)
            if data:
                self._timeout.reset()
                if data == '$':
                    isSentence = True
                    continue
                if data == '\r' or data == '\n':
                    isSentence = False
                    if sentence:
                        yield sentence
                        sentence = ''
                if isSentence:
                    sentence += data
            else:
                time.sleep(0.1)

    def __checksum(self, data):
        checksum = 0
        for char in data:
            checksum ^= ord(char)
        return "{0:02X}".format(checksum)

    def __global_fix(self, data):
        if data[6] in ['1', '2']:
            lat = self.__coord(data[2], data[3])
            lon = self.__coord(data[4], data[5])

            events.Post(self._queue).gps_location((lon, lat))

    def __sats(self, data):
        message = int(data[1])
        messages = int(data[1])
        viewed = int(data[3])

        if message == 1:
            self._sats.clear()

        blocks = (len(data) - 4) / 4
        for i in range(0, blocks):
            sat = int(data[4 + i * 4])
            level = data[7 + i * 4]
            used = True
            if level == '':
                level = None
                used = False
            else:
                level = int(level)
            self._sats[sat] = {'Level': level,
                               'Used': used}

        if message == messages and len(self._sats) == viewed:
            events.Post(self._queue).gps_satellites(self._sats)

    def __coord(self, coord, orient):
        pos = None

        if '.' in coord:
            if coord.index('.') == 4:
                try:
                    degrees = int(coord[:2])
                    minutes = float(coord[2:])
                    pos = degrees + minutes / 60.
                    if orient == 'S':
                        pos = -pos
                except ValueError:
                    pass
            elif coord.index('.') == 5:
                try:
                    degrees = int(coord[:3])
                    minutes = float(coord[3:])
                    pos = degrees + minutes / 60.
                    if orient == 'W':
                        pos = -pos
                except ValueError:
                    pass

        return pos

    def __open(self):
        self._timeout = Timeout(self.__timeout)
        self._comm = serial.Serial(self._gps.port,
                                   baudrate=self._gps.baud,
                                   bytesize=self._gps.bits,
                                   parity=self._gps.parity,
                                   stopbits=self._gps.stops,
                                   xonxoff=self._gps.soft,
                                   timeout=0)

    def __read(self):
        for resp in self.__serial_read():
            nmea = resp.split('*')
            if len(nmea) == 2:
                data = nmea[0].split(',')
                if data[0] in ['GPGGA', 'GPGSV']:
                    checksum = self.__checksum(nmea[0])
                    if checksum == nmea[1]:
                        if data[0] == 'GPGGA':
                            self.__global_fix(data)
                        elif data[0] == 'GPGSV':
                            self.__sats(data)
                    else:
                        warn = 'Invalid checksum for {} sentence'.format(data[0])
                        events.Post(self._queue).warning(warn)

    def __close(self):
        if self._timeout is not None:
            self._timeout.cancel()
        if self._comm is not None:
            self._comm.close()

    def run(self):
        try:
            self.__open()
            self.__read()
        except SerialException as error:
            events.Post(self._queue).gps_error(error.message)
        except OSError as error:
            events.Post(self._queue).gps_error(error)
        except ValueError as error:
            events.Post(self._queue).gps_error(error)

        self.__close()

    def stop(self):
        self._cancel = True


class Timeout(threading.Thread):
    def __init__(self, callback):
        threading.Thread.__init__(self)
        self.name = 'GPS Timeout'

        self._callback = callback
        self._done = threading.Event()
        self._reset = True

        self.start()

    def run(self):
        while self._reset:
            self._reset = False
            self._done.wait(TIMEOUT)

        if not self._done.isSet():
            self._callback()

    def reset(self):
        self._reset = True
        self._done.clear()

    def cancel(self):
        self._done.set()


if __name__ == '__main__':
    print 'Please run harrier.py'
    exit(1)
