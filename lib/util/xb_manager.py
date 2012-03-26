#! /usr/bin/env python
# -*- mode: python; indent-tabs-mode: nil; -*-
# vim:expandtab:shiftwidth=2:tabstop=2:smarttab:
#
# Copyright (C) 2011-2012 Patrick Crews, Valentine Gostev
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
import re
import subprocess

class xtrabackupManager:
    def __init__(self, server_manager, system_manager, variables):
        self.system_manager = system_manager
        self.code_manager = system_manager.code_manager
        self.server_manager = server_manager
        self.env_manager = system_manager.env_manager
        self.logging = system_manager.logging
        self.xb_bin_path = variables['xtrabackuppath']
        self.ib_bin_path = variables['innobackupexpath']
        self.backup_dir = os.path.join(variables['workdir'],'backups')

    def backup_full(self,server_object):
        self.datadir  = server_object.datadir
        self.ib_bin = self.xb_bin_path
        self.xb_bin = self.ib_bin_path
        self.b_root_dir = self.backup_dir
        self.b_path = os.path.join(self.b_root_dir, alloc_dir(self.b_root_dir))
        return self

    def alloc_dir(topdir, dir_pattern="backup"):
        dir_pattern_obj = dir_pattern + "(\\d+)"
        dir_pattern_obj = re.compile(dir_pattern_obj)
        for dirs in list(os.walk(topdir)):
            if list(dirs)[0] == topdir:
                dir_list = list(dirs)[1]
        
        for b in dir_list[:]:
            res = dir_pattern_obj.match(b)
            if not res:
                dir_list.remove(b)

        if dir_list == []:
            return_result = dir_pattern + '0'
            return return_result
        else:
            for a in dir_list[:]:
                dir_list.extend(re.split(dir_pattern,a))
                dir_list.remove(a)

            dir_list = filter(None, dir_list)
            dir_list.sort()
            return_result = dir_pattern + str(int(dir_list[len(dir_list)-1])+1)
            return return_result





def execute_cmd(cmd, exec_path, outfile_path):
    outfile = open(outfile_path,'w')
    cmd_subproc = subprocess.Popen( cmd
                                  , cwd = exec_path
                                  , shell=True
                                  , stdout = outfile 
                                  , stderr = subprocess.STDOUT 
                                  )
    cmd_subproc.wait()
    retcode = cmd_subproc.returncode 
    outfile.close
    in_file = open(outfile_path,'r')
    output = ''.join(in_file.readlines())
    return retcode,output


def innobackupex_backup( innobackupex_path
                       , xtrabackup_path
                       , output_path
                       , server
                       , backup_path
                       , extra_opts=None):
    """ Use the innobackupex binary specified at
        system_manager.innobackupex_path to take
        a backup of the given server

    """

    cmd = "%s --defaults-file=%s --user=root --port=%d --host=127.0.0.1 --ibbackup=%s %s" %( innobackupex_path
                                                                                           , server.cnf_file
                                                                                           , server.master_port
                                                                                           , xtrabackup_path
                                                                                           , backup_path)
    if extra_opts:
        cmd = ' '.join([cmd, extra_opts])
    exec_path = os.path.dirname(innobackupex_path)
    retcode, output = execute_cmd(cmd, exec_path, output_path)
    return retcode, output

def innobackupex_prepare( innobackupex_path
                        , xtrabackup_path
                        , output_path
                        , backup_path
                        , use_mem='500M'
                        , extra_opts=None):
    """ Use innobackupex to prepare an xtrabackup
        backup file

    """
    cmd = "%s --apply-log --use-memory=%s --ibbackup=%s %s" %( innobackupex_path
                                                             , use_mem
                                                             , xtrabackup_path
                                                             , backup_path)
    if extra_opts:
        cmd = ' '.join([cmd, extra_opts])
    exec_path = os.path.dirname(innobackupex_path)
    retcode, output = execute_cmd(cmd, exec_path, output_path)
    return retcode, output

def innobackupex_restore( innobackupex_path
                        , xtrabackup_path
                        , output_path
                        , backup_path
                        , cnf_file
                        , use_mem='500M'
                        , extra_opts=None):
    """ Use innobackupex to restore a server from
        a prepared xtrabackup backup

    """

    cmd = "%s --defaults-file=%s --copy-back --ibbackup=%s %s" %( innobackupex_path
                                                                , cnf_file
                                                                , xtrabackup_path
                                                                , backup_path
                                                                )
    if extra_opts:
        cmd = ' '.join([cmd, extra_opts])
    exec_path = os.path.dirname(innobackupex_path)
    retcode, output = execute_cmd(cmd, exec_path, output_path)
    return retcode, output




