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

import os
import shutil

from lib.util.mysqlBaseTestCase import mysqlBaseTestCase

server_requirements = [['--innodb-file-per-table'],['--innodb-file-per-table']]
servers = []
server_manager = None
test_executor = None
# we explicitly use the --no-timestamp option
# here.  We will be using a generic / vanilla backup dir
backup_path = None

class basicTest(mysqlBaseTestCase):


    def test_ib_incremental(self):
        master_server = servers[0]
        slave_server = servers[1]
        self.servers = servers
        logging = test_executor.logging
        xb_manager = test_executor.xtrabackup_manager
        # backup0 = xb_manager.backup_full(master_server)
        # xb_manager.prepare(backup0)
        # xb_manager.restore(backup0,master_server)
        randgen_manager = test_executor.randgen_manager
        randgen_manager.create_test_bed(master_server, optional_parameters)
        backup0 = xb_manager.backup_full(master_server)
        load0 = randgen_manager.create_load(master_server, runtime_options)
        load0.start()
        backup1 = xb_manager.backup_inc(master_server, backup0)
        xb_manager.prepare(backup0,rollback=False)
        xb_manager.prepare_inc(backup0,backup1)
        xb_manager.restore(slave_server)
        slave_server.start_repl(master_server)
        load0.wait()
        compare_checksums(master_server,slave_server,db1="test",db2="test2")




