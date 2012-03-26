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

server_requirements = [['--innodb-file-per-table']]
servers = []
server_manager = None
test_executor = None
# we explicitly use the --no-timestamp option
# here.  We will be using a generic / vanilla backup dir
backup_path = None

class basicTest(mysqlBaseTestCase):


    def test_ib_incremental(self):
        master_server = servers[0]
        self.servers = servers
        logging = test_executor.logging
        xb_manager = test_executor.xtrabackup_manager
        backup0 = xb_manager.backup_full(master_server)
        print(backup0.datadir)
        print(backup0.ib_bin, backup0.xb_bin)
        print(backup0.b_root_dir, backup0.b_path)
        backup1 = xb_manager.backup_full(master_server)
        print(backup1.datadir)
        print(backup1.ib_bin, backup1.xb_bin)
        print(backup1.b_root_dir, backup1.b_path)

 

