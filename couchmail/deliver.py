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

import sys
import os, os.path
import time
import hashlib
import email.parser
import couchdb.http, couchdb.client as couch

from couchmail.config import Config
from couchmail.logging import (debug, notice, warning, error, critical,
                               set_source, set_level)


def deliver ():
    config = Config.factory()
    set_source('deliver')
    set_level(config.get('logging_level'))

    try:
        recipient = sys.argv[1]
    except IndexError as e:
        error('No recipient specified.')
        return

    notice("Delivering mail for '%s'" % recipient)

    data = []
    size = 0
    while True:
        _data = sys.stdin.read(4096)
        if len(_data) == 0:
            break
        size += len(_data)
        if size > config.get('max_message_size'):
            error("Maximum message size exceeded.")
            sys.exit(-1)
        data.append(_data)
    data = ''.join(data)

    archive_dir = config.get('archive_dir')
    archive_file = False
    if not archive_dir == '':
        if not os.path.isdir(archive_dir):
            error("Archive dir not found")
        else:
            archive_file = os.path.join(archive_dir,
                    hashlib.sha1('%f' % time.time()).hexdigest())
            with open(archive_file, 'w') as fp:
                fp.write(data)
    
    parser = email.parser.FeedParser()
    parser.feed(data)
    message = parser.close()

    doc = dict([(a.lower(), b) for a, b in message.items()])
   
    payload = []
    for part in message.walk():
        if part.get_content_type() in ['text/plain', 'text/html']:
            payload.append({'content-type': part.get_content_type(),
                            'payload': part.get_payload()})

    doc['payload'] = payload
    doc['mailbox'] = 'inbox'
    doc['tags'] = []

    try:
        server = couch.Server('http://%s:%d' %
                (config.get('couchdb_host'),
                 config.get('couchdb_port')))
        users_db = server[config.get('couchdb_users')]
        db = server[users_db[recipient]['couchdb']]
        db.save(doc)
    except couchdb.http.ResourceNotFound as e:
        print e










