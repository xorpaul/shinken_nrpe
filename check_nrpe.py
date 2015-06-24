#!/usr/bin/python

import re, asyncore, socket, binascii, struct

class NRPEClient(asyncore.dispatcher):

    def __init__(self, host, command):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect( (host, 5666) )
        self.pktype = 0
        self.message = ''
        # We pack it, then we compute CRC32 of this first query
        query = struct.pack(">2hih1024scc", 02, 01, 0, 0, command, 'N', 'D')
        crc = binascii.crc32(query)

        # we restart with the crc value this time
        # because python2.4 do not have pack_into.
        self.buffer = struct.pack(">2hih1024scc", 02, 01, crc, 0, command, 'N', 'D')

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        data = self.recv(1034)
        print "len(data): %i" % len(data)
        print "self.pktype: %i" % self.pktype
        #if self.pktype != 2 or len(data) == 1034:
        if self.pktype != 2:
            version, pktype, crc, rc, response = struct.unpack(">2hih1024s", data)
            print "pktype: %i" % pktype
            self.message += re.sub('\x00.*$', '', response)
            print "setting self.pktype = %i" % pktype
            self.pktype = pktype

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]


client = NRPEClient('localhost', 'foobar')
#asyncore.loop()
while client.pktype != 2:
  asyncore.poll2(1)
print client.message
