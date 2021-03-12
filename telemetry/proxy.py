#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2018-2021 Vasily Evseenko <svpcom@p2ptech.org>

#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; version 3.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License along
#   with this program; if not, write to the Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division

from future import standard_library
standard_library.install_aliases()

from builtins import *

import struct
from . import mavlink
from twisted.python import log
from twisted.internet import reactor, defer
from twisted.internet.protocol import DatagramProtocol
from telemetry.conf import settings


class UDPProxyProtocol(DatagramProtocol):
    noisy = False

    def __init__(self, addr=None, agg_max_size=None, agg_timeout=None, inject_rssi=False):
        # use self.write to send mavlink message
        if inject_rssi:
            self.mav = mavlink.MAVLink(self, srcSystem=3, srcComponent=242) # WFB
        else:
            self.mav = None
        self.peer = None
        self.reply_addr = addr
        self.agg_max_size = agg_max_size
        self.agg_timeout = agg_timeout
        self.agg_queue = []
        self.agg_queue_size = 0
        self.agg_queue_timer = None

    def _cleanup(self):
        if(self.agg_queue_timer):
            self.agg_queue_timer.cancel()

    def flush_queue(self):
        if self.agg_queue_size > 0:
            if self.agg_queue_timer is not None \
               and not self.agg_queue_timer.called:
                self.agg_queue_timer.cancel()
            self.agg_queue_timer = None
            self._send_to_peer(b''.join(self.agg_queue))
            self.agg_queue = []
            self.agg_queue_size = 0

    # call from peer and from mavlink rssi injector only!
    def write(self, msg):
        if self.transport is None or self.reply_addr is None:
            return

        if self.agg_max_size is None or self.agg_timeout is None:
            self.transport.write(msg, self.reply_addr)
            return

        # Split batch of mavlink packets due to issues with mavlink-router

        i = 0
        while i < len(msg):
            if len(msg) - i < 8:
                log.msg('Too short mavlink packet: %r' % (msg[i:],))
                break

            version = struct.unpack('B', msg[i : i + 1])[0]

            # mavlink 1
            if version == 0xfe:
                mlen = 8 + struct.unpack('B', msg[i + 1 : i + 2])[0]
                self.transport.write(msg[i: i + mlen], self.reply_addr)
                i += mlen

            # mavlink 2
            elif version == 0xfd:
                mlen, flags = struct.unpack('BB', msg[i + 1 : i + 3])

                if flags & ~0x01:
                    log.msg('Unsupported mavlink flags: 0x%x' % (flags,))
                    self.transport.write(msg[i:], self.reply_addr)
                    break

                mlen += (25 if flags & 0x01 else 12)
                self.transport.write(msg[i : i + mlen], self.reply_addr)
                i += mlen

            else:
                log.msg('Unsupported mavlink version: 0x%x' % (version,))
                self.transport.write(msg[i:], self.reply_addr)
                break

    def _send_to_peer(self, data):
        if self.peer is not None:
            self.peer.write(data)

    def datagramReceived(self, data, addr):
        if settings.common.debug:
            log.msg('Got a message from %s' % (addr,))

        self.reply_addr = addr

        # send message to local transport
        if self.agg_max_size is None or self.agg_timeout is None:
            return self._send_to_peer(data)

        if len(data) > self.agg_max_size:
            log.msg('Message too big: %d > %d' % (len(data), self.agg_max_size), isError=1)
            return

        if self.agg_queue_size + len(data) > self.agg_max_size:
            # message doesn't fit into agg queue
            if self.agg_queue_timer is not None:
                self.agg_queue_timer.cancel()
                self.agg_queue_timer = None

            self._send_to_peer(b''.join(self.agg_queue))
            self.agg_queue = []
            self.agg_queue_size = 0

        self.agg_queue.append(data)
        self.agg_queue_size += len(data)

        if self.agg_timeout and self.agg_queue_timer is None:
            self.agg_queue_timer = reactor.callLater(self.agg_timeout, self.flush_queue)


    def send_rssi(self, rssi, rx_errors, rx_fec, flags):
        # Send flags as remnoise, because txbuf value is used by PX4 to throttle bandwidth
        if self.mav is not None:
            self.mav.radio_status_send(rssi, rssi, 100, 0, flags, rx_errors, rx_fec)

