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

import time

from lib.util.mysqlBaseTestCase import mysqlBaseTestCase
from percona_tests.cluster_basic import suite_config

server_requirements = suite_config.server_requirements
server_requests = suite_config.server_requests
servers = suite_config.servers 
test_executor = suite_config.test_executor 

class basicTest(mysqlBaseTestCase):

    def test_replace(self):
        self.servers = servers
        logging = test_executor.logging
        master_server = servers[0]
        other_nodes = servers[1:] # this can be empty in theory: 1 node
        time.sleep(5)

        queries = [  "CREATE TABLE t1(a INT NOT NULL AUTO_INCREMENT, b INT NOT NULL, c CHAR(100), d CHAR(20), PRIMARY KEY(a))"
                   , "INSERT INTO t1 (b,c,d) VALUES (10,'a','f'),(20,'b','e'),(30,'c','d'),(40,'d','c'),(50,'e','b'),(60,'f','a')"
                   , "CREATE TABLE t2 LIKE t1"
                   , "INSERT INTO t2  SELECT a, b*20, CONCAT(c,'replace'), CONCAT(d, 'replace_too') FROM t1"
                   , "REPLACE INTO t1 SELECT * FROM t2"
                  ]
        for query in queries:
            retcode, result = self.execute_query(query, master_server)
            self.assertEqual( retcode, 0, result)
        # check 'master'
        query = "SELECT * FROM t1"
        retcode, master_result_set = self.execute_query(query, master_server)
        self.assertEqual(retcode,0, master_result_set)
        expected_result_set = ( (1L, 200L, 'areplace', 'freplace_too')
                              , (4L, 400L, 'breplace', 'ereplace_too')
                              , (7L, 600L, 'creplace', 'dreplace_too')
                              , (10L, 800L, 'dreplace', 'creplace_too')
                              , (13L, 1000L, 'ereplace', 'breplace_too')
                              , (16L, 1200L, 'freplace', 'areplace_too')) 
        self.assertEqual( master_result_set
                        , expected_result_set
                        , msg = (master_result_set, expected_result_set)
                        )
        master_slave_diff = self.check_slaves_by_checksum( master_server
                                                         , other_nodes
                                                         )
        self.assertEqual(master_slave_diff, None, master_slave_diff)
        