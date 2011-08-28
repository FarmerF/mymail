# This file is part of Couchmail.
# 
# Couchmail is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Couchmail is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with Couchmail.  If not, see <http://www.gnu.org/licenses/>.
# 
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
"""This module provides configuration services.


"""

import ConfigParser
import pyinotify
import os, os.path

manager = pyinotify.WatchManager()
notifier = pyinotify.ThreadedNotifier(manager)
notifier.setDaemon(notifier)
notifier.start()


class Config (ConfigParser.SafeConfigParser):

    """Thin wrapper around ConfigParser.

    A thin wrapper around SafeConfigParser that offers 2 additional 
    features:
        - Persistent reusable config files (use the factory function),
        - Auto-reloading when a file changes.
    
    Be adviced that any changes made to this object are readable by
    any other process that holds the same instances. Also any changes
    will be overwritten by the auto-reload function, as such, treat this
    object as read-only.

    """
    
    _instance = None

    @classmethod
    def _config_file_changed (cls, event):
        """Event handler for pyinofity"""
        if cls._instance is None:
            return
        if event.pathname == cls._instance.configfile:
            print "reload"
            cls._instance = Config(cls._instance.configfile)

    @classmethod
    def factory (cls, configfile=None):
        """Returns a config object for the requested file.

        If an instance of this file is already loaded that
        instance is returned, otherwise a new one is created.
        It is important to treat these config instances as read-only
        objects. Any changes may be overwritten by the autoreload
        process.

        """
        if configfile is None:
            configfile = os.getenv('COUCHMAIL_CONFIG', 'couchmail.conf')
        configfile = os.path.abspath(configfile)

        if not os.path.isfile(configfile):
            configfile = None
        
        if cls._instance is None:
            try:
                instance = Config(configfile)
                if not configfile is None:
                    instance.read(configfile)
            except Exception as e:
                raise e
            except ConfigParser.Error as e:
                raise e
            
            cls._instances = instance

            if not configfile is None:
                enclosing_dir = os.path.abspath(os.path.dirname(configfile))
                manager.add_watch(enclosing_dir, pyinotify.IN_MODIFY,
                        proc_fun=cls._config_file_changed)
        return cls._instance
    
    def __init__ (self, configfile):
        ConfigParser.ConfigParser.__init__(self, {
                'couchdb_host': 'localhost',
                'couchdb_port': 5984,
                'couchdb_users': 'users',
                'couchdb_sessions': 'sessions',
                'couchdb_logs': 'logs',
                'logging_level': 3, # Error level
                'logging_debug': False,
            })
        self.configfile = configfile
