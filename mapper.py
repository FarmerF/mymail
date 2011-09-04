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

"""Module docstring"""

import SocketServer
import sys
import couchdb.http
import couchdb.client as couch

from couchmail.config import Config
from couchmail.logging import (debug, notice, warning, error, 
                               critical, set_source, set_level)


class MapHandler (SocketServer.BaseRequestHandler):

    def handle (self):
        try:
            raw_data = self.request.recv(4096)
        except Exception as e:
            error("Error reading from socket '%s'" % e)
            return

        parts = [x.strip() for x in raw_data.split(' ')]

        if not parts[0] == 'get':
            notice("Geen get '%s'" % str(parts))
            self.request.send('400 Not implemented.\n')
            return

        data = []
        i = 0
        while i < len(parts[1]):
            if parts[1][i] == '%':
                try:
                    code = int('0x%s' % parts[1][i+1:i+3], 0)
                    data.append(chr(code))
                    i += 3
                except ValueError as e:
                    notice("Error parsing input '%s'" % str(parts))
                    self.request.send("500 Invalid escape sequence\n")
                    return
                except IndexError as e:
                    notice("Error parsing input '%s'" % str(parts))
                    self.request.send("500 Invalid escape sequence\n")
                    return
            else:
                data.append(parts[1][i])
                i += 1

        data = ''.join(data)
        
        print data
        config = Config.factory()

        if data.find('@') < 0:
            if data == 'sigma.student.utwente.nl':
                self.request.send('200 sigma.student.utwente.nl\n')
                return

        try:
            server = couch.Server('http://%s:%s' % 
                    (config.get('couchdb_host'),
                     config.get('couchdb_port')))
            db = server[config.get('couchdb_users')]
            view = db.view('users/aliasses', key=data)
            if not len(view) == 1:
                self.request.send("500 Alias unknown\n")
                return
            else:
                self.request.send("200 %s\n" % view.rows[0].value)
        except couchdb.http.ResourceNotFound as e:
            print e

def main ():
    config = Config.factory()
    set_source('mapper')
    set_level(config.get('logging_level'))
    try:
        server = SocketServer.TCPServer(('localhost', 31337), MapHandler)
        server.serve_forever()
    except Exception as e:
        print e
        critical("Caught exception '%s'" % e)
        sys.exit(-1)


if __name__ == '__main__':
    main()
