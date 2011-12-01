#! /usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; -*-
# vim:expandtab:shiftwidth=2:tabstop=2:smarttab:
#
# Copyright (C) 2010,2011 Patrick Crews
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


""" mysqld.py:  code to allow a serverManager
    to provision and start up a mysqld server object
    for test execution

"""

# imports
import os
import sys
import time
import subprocess

from ConfigParser import RawConfigParser

import MySQLdb

from lib.server_mgmt.server import Server
from lib.util.mysql_methods import execute_query

class mysqlServer(Server):
    """ represents a mysql server, its possessions
        (datadir, ports, etc), and methods for controlling
        and querying it

        TODO: create a base server class that contains
              standard methods from which we can inherit
              Currently there are definitely methods / attr
              which are general

    """

    def __init__( self, name, server_manager, code_tree, default_storage_engine
                , server_options, requester, test_executor, workdir_root):
        super(mysqlServer, self).__init__( name
                                           , server_manager
                                           , code_tree
                                           , default_storage_engine
                                           , server_options
                                           , requester
                                           , test_executor
                                           , workdir_root)
        self.preferred_base_port = 9306
        
        # client files
        self.mysqldump = self.code_tree.mysqldump
        self.mysqladmin = self.code_tree.mysqladmin
        self.mysql_client = self.code_tree.mysql_client
        self.mysqlimport = self.code_tree.mysqlimport
        self.mysqlslap = self.code_tree.mysqlslap
        self.mysql_upgrade = self.code_tree.mysql_upgrade
        self.server_path = self.code_tree.mysql_server
        self.mysql_client_path = self.code_tree.mysql_client
      
        # important stuff
        self.langdir = self.code_tree.langdir
        self.charsetdir = self.code_tree.charsetdir
        self.bootstrap_file = self.code_tree.bootstrap_path
        self.bootstrap_cmd = None

        # Get our ports
        self.port_block = self.system_manager.port_manager.get_port_block( self.name
                                                                         , self.preferred_base_port
                                                                         , 1 )
        self.master_port = self.port_block[0]

        # Generate our working directories
        self.dirset = { 'var_%s' %(self.name): {'std_data_ln':( os.path.join(self.code_tree.testdir,'std_data'))
                                               ,'log':None
                                               ,'run':None
                                               ,'tmp':None
                                               ,'master-data': { 'test':None
                                                               , 'mysql':None
                                                               }
                                               }  
                      }
        self.workdir = self.system_manager.create_dirset( workdir_root
                                                        , self.dirset)
        self.vardir = self.workdir
        self.tmpdir = os.path.join(self.vardir,'tmp')
        self.rundir = os.path.join(self.vardir,'run')
        self.logdir = os.path.join(self.vardir,'log')
        self.std_data = os.path.join(self.vardir,'std_data_ln')
        self.datadir = os.path.join(self.vardir,'master-data')

        self.error_log = os.path.join(self.logdir,('error.log'))
        self.bootstrap_log = os.path.join(self.logdir,('bootstrap.log'))
        self.pid_file = os.path.join(self.rundir,('%s.pid' %(self.name)))
        self.socket_file = os.path.join(self.vardir, ('%s.sock' %(self.name)))
        self.timer_file = os.path.join(self.logdir,('timer'))
        self.general_log_file = os.path.join(self.logdir,'mysqld.log')
        self.slow_query_log_file = os.path.join(self.logdir,'mysqld-slow.log')
        self.cnf_file = os.path.join(self.vardir,'my.cnf')

        self.snapshot_path = os.path.join(self.tmpdir,('snapshot_%s' %(self.master_port)))
        # We want to use --secure-file-priv = $vardir by default
        # but there are times / tools when we need to shut this off
        if self.no_secure_file_priv:
            self.secure_file_string = ''
        else:
            self.secure_file_string = "--secure-file-priv='%s'" %(self.vardir)
        self.user_string = '--user=root'

        self.initialize_databases()
        self.take_db_snapshot()

        self.logging.debug_class(self)


    def report(self):
        """ We print out some general useful info """
        report_values = [ 'name'
                        , 'master_port'
                        , 'socket_file'
                        , 'vardir'
                        , 'status'
                        ]
        self.logging.info("%s server:" %(self.owner))
        for key in report_values:
          value = vars(self)[key] 
          self.logging.info("%s: %s" %(key.upper(), value))

    def initialize_databases(self):
        """ Do the voodoo required to have a working database setup.
            For MySQL, this is calling the server with the 
            --bootstrap argument.  We generate the bootstrap
            file during codeTree intialization as the file is standard for
            all MySQL servers that are spawned from a single codeTree

        """
  
        # generate the bootstrap startup command
        if not self.bootstrap_cmd:
            mysqld_args = [ "--no-defaults"
                          , "--bootstrap"
                          , "--basedir=%s" %(self.code_tree.basedir)
                          , "--datadir=%s" %(self.datadir)
                          , "--loose-skip-falcon"
                          , "--loose-skip-ndbcluster"
                          , "--tmpdir=%s" %(self.tmpdir)
                          , "--core-file"
                          , "--lc-messages-dir=%s" %(self.langdir)
                          , "--character-sets-dir=%s" %(self.charsetdir)
                          ]
            # We add server_path into the mix this way as we
            # may alter how we store / handle server args later
            mysqld_args.insert(0,self.server_path)
            self.bootstrap_cmd = " ".join(mysqld_args)
        # execute our command
        bootstrap_log = open(self.bootstrap_log,'w')
        # open our bootstrap file
        bootstrap_in = open(self.bootstrap_file,'r')
        bootstrap_subproc = subprocess.Popen( self.bootstrap_cmd
                                            , shell=True
                                            , stdin=bootstrap_in
                                            , stdout=bootstrap_log
                                            , stderr=bootstrap_log
                                            )
        bootstrap_subproc.wait()
        bootstrap_in.close()
        bootstrap_log.close()
        bootstrap_retcode = bootstrap_subproc.returncode
        if bootstrap_retcode:
            self.logging.error("Received retcode: %s executing command: %s"
                               %(bootstrap_retcode, self.bootstrap_cmd))
            self.logging.error("Check the bootstrap log: %s" %(self.bootstrap_log))
            sys.exit(1)


    def get_start_cmd(self):
        """ Return the command string that will start up the server 
            as desired / intended
 
        """

        server_args = [ self.process_server_options()
                      , "--open-files-limit=1024"
                      , "--local-infile"
                      , "--character-set-server=latin1"
                      , "--connect-timeout=60"
                      , "--log-bin-trust-function-creators=1"
                      , "--key_buffer_size=1M"
                      , "--sort_buffer=256K"
                      , "--max_heap_table_size=1M"
                      , "--loose-innodb_data_file_path=ibdata1:10M:autoextend"
                      , "--loose-innodb_buffer_pool_size=8M"
                      , "--loose-innodb_write_io_threads=2"
                      , "--loose-innodb_read_io_threads=2"
                      , "--loose-innodb_log_buffer_size=1M"
                      , "--loose-innodb_log_file_size=5M"
                      , "--loose-innodb_additional_mem_pool_size=1M"
                      , "--loose-innodb_log_files_in_group=2"
                      , "--slave-net-timeout=120"
                      , "--log-bin=%s" %(os.path.join(self.logdir,"mysqld-bin"))
                      , "--loose-enable-performance-schema"
                      , "--loose-performance-schema-max-mutex-instances=10000"
                      , "--loose-performance-schema-max-rwlock-instances=10000"
                      , "--loose-performance-schema-max-table-instances=500"
                      , "--loose-performance-schema-max-table-handles=1000"
                      , "--binlog-direct-non-transactional-updates"
                      , "--loose-enable-performance-schema"
                      , "--general_log=1"
                      , "--general_log_file=%s" %(self.general_log_file)
                      , "--slow_query_log=1"
                      , "--slow_query_log_file=%s" %(self.slow_query_log_file)
                      , "--basedir=%s" %(self.code_tree.basedir)
                      , "--datadir=%s" %(self.datadir)
                      , "--tmpdir=%s"  %(self.tmpdir)
                      , "--character-sets-dir=%s" %(self.charsetdir)
                      , "--lc-messages-dir=%s" %(self.langdir)
                      , "--ssl-ca=%s" %(os.path.join(self.std_data,'cacert.pem'))
                      , "--ssl-cert=%s" %(os.path.join(self.std_data,'server-cert.pem'))
                      , "--ssl-key=%s" %(os.path.join(self.std_data,'server-key.pem'))
                      , "--port=%d" %(self.master_port)
                      , "--socket=%s" %(self.socket_file)
                      , "--pid-file=%s" %(self.pid_file)
                      , "--default-storage-engine=%s" %(self.default_storage_engine)
                      # server-id maybe needs fixing, but we want to avoid
                      # the server-id=0 and no replication thing...
                      , "--server-id=%d" %(self.get_numeric_server_id()+1)
                      , self.secure_file_string
                      , self.user_string
                      ]
        self.gen_cnf_file(server_args)

        if self.gdb:
            server_args.append('--gdb')
            return self.system_manager.handle_gdb_reqs(self, server_args)
        else:
            return "%s %s %s & " % ( self.cmd_prefix
                                   , self.server_path
                                   , " ".join(server_args)
                                   )


    def get_stop_cmd(self):
        """ Return the command that will shut us down """
        
        return "%s --no-defaults --user=root --port=%d --host=127.0.0.1 --protocol=tcp shutdown " %(self.mysqladmin, self.master_port)
           

    def get_ping_cmd(self):
        """Return the command string that will 
           ping / check if the server is alive 

        """

        return '%s --no-defaults --user=root --port=%d --host=127.0.0.1 --protocol=tcp ping' % (self.mysqladmin, self.master_port)

    def is_started(self):
        """ Determine if the server is up and running - 
            this may vary from server type to server type

        """

        # We experiment with waiting for a pid file to be created vs. pinging
        # This is what test-run.pl does and it helps us pass logging_stats tests
        # while not self.ping_server(server, quiet=True) and timer != timeout:

        return self.system_manager.find_path( [self.pid_file]
                                            , required=0)

    def gen_cnf_file(self, server_args):
        """ We generate a .cnf file for the server based
            on the arguments.  We currently don't use
            this for much, but xtrabackup uses it, so 
            we must produce one.  This could also be
            helpful for testing / etc

        """

        config_file = open(self.cnf_file,'w')
        config_file.write('[mysqld]') 
        for server_arg in server_args:
            # We currently have a list of string values
            # We need to remove any '--' stuff 
            server_arg = server_arg.replace('--','')+'\n'
            config_file.write(server_arg)
        config_file.close() 

    def set_master(self, master_server, get_cur_log_pos = True):
        """ We do what is needed to set the master_server
            as the replication master

        """

        if self.status:  # we are running and can do things!
            # Get master binlog info
            master_binlog_file, master_binlog_pos = master_server.get_binlog_info()
            if not get_cur_log_pos:
                master_binlog_pos = 0
            
            # update our slave's master info
            query = ("CHANGE MASTER TO "
                     "MASTER_HOST='127.0.0.1',"
                     "MASTER_USER='root',"
                     "MASTER_PASSWORD='',"
                     "MASTER_PORT=%d,"
                     "MASTER_LOG_FILE='%s',"
                     "MASTER_LOG_POS=%d" % ( master_server.master_port
                                           , master_binlog_file
                                           , int(master_binlog_pos)))
            retcode, result_set = execute_query(query, self)
            if retcode:
                self.logging.error("Could not set slave: %s.%s\n"
                                   "With query: %s\n."
                                   "Returned result: %s" %( self.owner
                                                          , self.name
                                                          , query
                                                          , result_set)
                                  )
                return 1
            # start the slave
            query = "START SLAVE"
            retcode, result_set = execute_query(query, self)
            if retcode:
                self.logging.error("Could not set slave: %s.%s\n" 
                                   "With query: %s\n."
                                   "Returned result: %s" %( self.owner
                                                          , self.name
                                                          , query
                                                          , result_set)
                                  )
                return 1
            self.need_to_set_master = False
        else:
            self.need_to_set_master = True 
            self.master = master_server
        return 0

    def get_binlog_info(self):
        """ We try to get binlog information for the server """
        query = "SHOW MASTER STATUS"
        retcode, result_set = execute_query(query, self)
        binlog_file = result_set[0][0]
        binlog_pos = result_set[0][1]
        return binlog_file, binlog_pos

