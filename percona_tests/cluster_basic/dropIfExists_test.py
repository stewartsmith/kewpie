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
import os
import time

from lib.util.mysqlBaseTestCase import mysqlBaseTestCase

server_requirements = [[],[],[]]
server_requests = {'join_cluster':[(0,1), (0,2)]}
servers = []
server_manager = None
test_executor = None

class basicTest(mysqlBaseTestCase):

    def test_drop(self):
        self.servers = servers
        master_server = servers[0]
        other_nodes = servers[1:] # this can be empty in theory: 1 node
        time.sleep(5)

        queries = [ ("CREATE TABLE t1(a INT NOT NULL, PRIMARY KEY(a)) "
                     "Engine=Innodb " )
                   ,"INSERT INTO t1 VALUES (42)"
                   ,"INSERT INTO t1 VALUES (1)"
                   ,"INSERT INTO t1 VALUES (2)"
                   ,"DROP TABLE IF EXISTS t1" 
                   ,"DROP TABLE IF EXISTS t_nothere"
                  ]
        retcode, result = self.execute_queries(queries, master_server)
        self.assertEqual( retcode, 0, result)
        # check 'master'
        query = "SHOW TABLES IN test"
        retcode, master_result_set = self.execute_query(query, master_server)
        self.assertEqual(retcode,0, master_result_set)
        expected_result_set = ()
        self.assertEqual( master_result_set
                        , expected_result_set
                        , msg = (master_result_set, expected_result_set)
                        )
        master_slave_diff = self.check_slaves_by_query( master_server
                                                 , other_nodes
                                                 , query
                                                 , expected_result = expected_result_set
                                                 )
        self.assertEqual(master_slave_diff, None, master_slave_diff)
        
