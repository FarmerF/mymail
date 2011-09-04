from couchdb.client import Server
import sys

s = Server()
db = s[sys.argv[1]]
for _id in db:
    if not _id[0] == '_':
        del db[_id]
