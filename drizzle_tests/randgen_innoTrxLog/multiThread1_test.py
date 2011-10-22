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

from lib.util.randgen_methods import execute_randgen

server_requirements = [['--innodb.replication-log'],[]]
servers = []
server_manager = None
test_executor = None

class multithread1Test(unittest.TestCase):

    #def setUp(self):
    #    """ If we need to do anything pre-test, we do it here.
    #        Any code here is executed before any test method we
    #        may execute
    #
    #    """

    #    return


    def test_multithread1(self):
        test_cmd = "./gentest.pl --gendata=conf/drizzle/translog_drizzle.zz --grammar=conf/drizzle/translog_concurrent1.yy --Reporter=DrizzleInnoTrxLog  --queries=100 --threads=3"
        retcode, output = execute_randgen(test_cmd, test_executor, servers)
        self.assertTrue(retcode==0, output)

    def tearDown(self):
            server_manager.reset_servers(test_executor.name)


def run_test(output_file):
    suite = unittest.TestLoader().loadTestsFromTestCase(multithread1Test)
    return unittest.TextTestRunner(stream=output_file, verbosity=2).run(suite)

