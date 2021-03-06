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

import ConfigParser
import sys

from wildfind.harrier.comm import Comm


class Settings(object):
    def __init__(self, args):

        self.db = args.file

        self.delay = None

        self.survey = args.survey
        self.freq = args.frequency
        self.test = args.test

        self.recvIndex = 0
        self.recvGain = 0
        self.recvCal = 0

        self.gps = Comm()

        self.__load_conf(args)

    def __load_conf(self, args):

        config = ConfigParser.SafeConfigParser()

        try:
            config.read(args.conf)

            if config.has_option('scan', 'delay'):
                self.delay = config.getint('scan', 'delay')

            if config.has_option('receiver', 'index'):
                self.recvIndex = config.getint('receiver', 'index')

            if args.gain is not None:
                self.recvGain = args.gain
            elif config.has_option('receiver', 'gain'):
                self.recvGain = config.getfloat('receiver', 'gain')

            if config.has_option('receiver', 'calibration'):
                self.recvCal = config.getfloat('receiver', 'calibration')

            self.gps.port = config.get('gps', 'port')

            if config.has_option('gps', 'baud'):
                bauds = self.gps.get_bauds()
                baud = config.getint('gps', 'baud')
                if baud in bauds:
                    self.gps.baud = baud
                else:
                    raise ValueError('Baud "{}" is not one of:\n  {}'.format(baud,
                                                                             bauds))

            if config.has_option('gps', 'bits'):
                bits = config.getint('gps', 'bits')
                if bits in Comm.BITS:
                    self.gps.bits = bits
                else:
                    raise ValueError('Bits "{}" is note one of:\n  {}'.format(bits,
                                                                              Comm.BITS))

            if config.has_option('gps', 'parity'):
                parity = config.get('gps', 'parity')
                if parity in Comm.PARITIES:
                    self.gps.parity = parity
                else:
                    raise ValueError('Parity "{}" is not one of:\n  {}'.format(parity,
                                                                               Comm.PARITIES))

            if config.has_option('gps', 'stops'):
                stops = config.getfloat('gps', 'stops')
                if stops in Comm.STOPS:
                    self.gps.stops = stops
                else:
                    raise ValueError('Stops "{}" is not one of:\n  {}'.format(stops,
                                                                              Comm.STOPS))

            if config.has_option('gps', 'soft'):
                self.gps.soft = config.getboolean('gps', 'soft')

        except ConfigParser.Error as error:
            sys.stderr.write('Configuration error: {}\n'.format(error))
            exit(2)
        except ValueError as error:
            sys.stderr.write('Configuration error: {}\n'.format(error))
            exit(2)

    def get(self):
        settings = {'port': self.gps.port,
                    'delay': self.delay,
                    'frequency': self.freq}
        return settings


if __name__ == '__main__':
    print 'Please run harrier.py'
    exit(1)
