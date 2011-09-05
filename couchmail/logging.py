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

"""Logging module."""
import couchdb.client as couch
import couchdb.http
import time

import couchmail.config

__all__ = ['Level', 'set_source', 'log', 'debug',
        'notice', 'warning', 'error']

class Level (object):
    DEBUG = 1
    NOTICE = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

str_level = ['stub', 'debug', 'notice', 'warning', 'error', 'critical']

config = couchmail.config.Config.factory()
log_db = None
source = 'unknown'

def set_source (new_source):
    """Set a source.
    
    Source should be a short string that identifies the source of
    this log message.

    """
    global source
    source = new_source

def log (level, msg, info={}):
    """Enter a message into the log.

    Messages with level < log_level are ignored (unless the 
    debug flag is turned in which case they are printed).

    """
    global log_db

    if level < 1 or level > 5:
        raise ValueError("Invalid debug level.")
    if config.get('logging_debug'):
        print "[%s] %s:  %s" % (str_level[level], time.asctime(), msg)

    if level < config.get('logging_level'):
        return

    if log_db is None:
        server = couch.Server('http://%s:%d' % (config.get('couchdb_host'),
            config.get('couchdb_port')))
        try:
            log_db = server[config.get('couchdb_logs')]
        except couchdb.http.ResourceNotFound as e:
            raise e

    doc = dict({
           'level': level,
           'str_level': str_level[level],
           'utc': time.asctime(),
           'timestamp': time.time(),
           'message': msg,
           'source': source,
           }.items() + info.items())
    log_db.save(doc) 

def debug (msg, info={}):
    """Record a debug message.

    Debug messages are meant to aid in debugging problems. This
    level should be turned off in production installations.

    """
    log(Level.DEBUG, msg, info)

def notice (msg, info={}):
    """Record a notice.

    Notices should be used to record non-error situations, they
    should be used to obtain information about program flow.

    """
    log(Level.NOTICE, msg, info)

def warning (msg, info={}):
    """Record a warning.

    Warnings should be used in situations where somthing happens
    that is not an error condition, but the user should try to avoid
    the situation nonetheless.

    """
    log(Level.WARNING, msg, info)

def error (msg, info={}):
    """Record an error message.

    Error messages should be used when an error occurs that the program
    can recover from.

    """
    log(Level.ERROR, msg, info)

def critical (msg, info={}):
    """Record a critical error.

    Critical errors should be used when to program encounters a problem
    that forces it to abort immediatly, it is the program's own 
    responsibility to exit.

    """
    log(Level.CRITICAL, msg, info)
