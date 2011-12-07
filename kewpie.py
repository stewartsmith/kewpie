#! /usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; -*-
# vim:expandtab:shiftwidth=2:tabstop=2:smarttab:
#
# Copyright (C) 2010 Patrick Crews
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


""" kewpie.py

(DataBase) Quality Platform - system for executing various
testing systems and the helper code 

Designed to be a modular test-runner.  Different testing tools
and databases may be plugged into the system via hacking the
appropriate modules

Currently geared towards Drizzle and MySQL systems
Runs: Drizzle, MySQL, Percona Server, Galera dbms's
"""

# imports
import os
import sys

import lib.opts.test_run_options as test_run_options
from lib.modes.test_mode import handle_mode
from lib.server_mgmt.server_management import serverManager
from lib.sys_mgmt.system_management import systemManager
from lib.test_mgmt.execution_management import executionManager

# functions

# main
# We base / look for a lot of things based on the location of
# the kewpie.py file
qp_rootdir = os.path.dirname(os.path.abspath(sys.argv[0]))
basedir_default = os.path.dirname(qp_rootdir)
testdir_default = qp_rootdir
defaults = { 'qp_root':qp_rootdir
           , 'testdir': qp_rootdir
           , 'workdir': os.path.join(qp_rootdir,'workdir')
           , 'clientbindir': os.path.join(os.path.dirname(qp_rootdir),'client')
           , 'basedir':os.path.dirname(qp_rootdir)
           , 'server_type':'mysql'
           , 'valgrind_suppression':os.path.join(qp_rootdir,'valgrind.supp')
           , 'suitepaths': [ os.path.join(basedir_default,'plugin')
                           , os.path.join(testdir_default,'suite')
                           ]
           , 'randgen_path': os.path.join(qp_rootdir,'randgen')
           , 'subunit_file': os.path.join(qp_rootdir,'workdir/test_results.subunit')
           }
variables = test_run_options.parse_qp_options(defaults)
variables['qp_root'] = qp_rootdir
system_manager = None
server_manager = None
test_manager = None
test_executor = None
execution_manager = None

try:
        # Some system-level work is constant regardless
        # of the test to be run
        system_manager = systemManager(variables)

        # Create our server_manager
        server_manager = serverManager(system_manager, variables)

        # Get our mode-specific test_manager and test_executor
        (test_manager,test_executor) = handle_mode(variables, system_manager)

        # Gather our tests for execution
        test_manager.gather_tests()

        # Initialize test execution manager
        execution_manager = executionManager(server_manager, system_manager
                                        , test_manager, test_executor
                                        , variables)

        # Execute our tests!
        execution_manager.execute_tests()
    
except Exception, e:
       print Exception, e

except KeyboardInterrupt:
      print "\n\nDetected <Ctrl>+c, shutting down and cleaning up..."

finally:
# TODO - make a more robust cleanup
# At the moment, runaway servers are our biggest concern
    if server_manager and not variables['startandexit']:
        if variables['gdb']:
            server_manager.cleanup_all_servers()
        else:
            server_manager.cleanup()
    if not variables['startandexit']:
        if test_manager:
            fail_count = test_manager.has_failing_tests()
            sys.exit(test_manager.has_failing_tests())
        else:
            # return 1 as we likely have a problem if we don't have a
            # test_manager
            sys.exit(1)

