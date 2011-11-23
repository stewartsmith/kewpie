#! /usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; -*-
# vim:expandtab:shiftwidth=2:tabstop=2:smarttab:
#
# Copyright (C) 2011 Patrick Crews
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import unittest
import subprocess
import os

from lib.util.mysqlBaseTestCase import mysqlBaseTestCase

server_requirements = [[]]
servers = []
server_manager = None
test_executor = None

class basicTest(mysqlBaseTestCase):

    def test_OuterJoin1(self):
        self.servers = servers
        test_cmd = "./gentest.pl --gendata=conf/percona/outer_join_percona.zz --grammar=conf/percona/outer_join_percona.yy --queries=500 --threads=5"
        retcode, output = self.execute_randgen(test_cmd, test_executor, servers)
        self.assertTrue(retcode==0, output)

