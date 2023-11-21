#!/usr/bin/python3
from twisted.internet import reactor, protocol
import sys

class Client(protocol.Protocol):

    def __init__(self, s):
        self.server = s
        self.connected = 0
        self.data = []

    def connectionMade(self):
        self.connected = 1
        for a in self.data:
            self.transport.write(a)
        self.data = []

    def write(self, a):
        if self.connected:
            self.transport.write(a)
        else:
            self.data.append(a)

    def dataReceived(self, a):
        self.server.write(a)
        print(self.server.i, 'S', formatbytes(a))

    def connectionLost(self, reason=''):
        if self.server.client:
            print('Connection', self.server.i, 'lost from server')
            self.server.transport.loseConnection()
        self.server = None

class ClientFactory(protocol.ClientFactory):

    def __init__(self, c):
        self.client = c

    def buildProtocol(self, a):
        return self.client

class Server(protocol.Protocol):

    def __init__(self):
        global i
        self.i = i = i + 1
        self.client = Client(self)
        print('Connection', i, 'initialized')

    def connectionMade(self):
        reactor.connectTCP(sys.argv[1], int(sys.argv[2]), ClientFactory(self.client))

    def dataReceived(self, a):
        self.client.write(a)
        print(self.i, 'C', formatbytes(a))

    def write(self, a):
        self.transport.write(a)

    def connectionLost(self,reason=1):
        if self.client.server:
            print('Connection', self.i, 'lost from client')
            self.client.transport.loseConnection()
        self.client = None

class ServerFactory(protocol.ServerFactory):
    protocol = Server

def highlight(byt):
    table = {0:'000', 1:'001', 2:'002', 3:'003', 4:'004', 5:'005', 6:'006', 7:'a', 8:'b', 9:'t', 10:'n', 11:'v', 12:'f', 13:'r'}
    i = 0
    out = 'b\''
    pb = False
    for a in byt:
        if a >= 32 and a <= 126:
            if pb:
                out += '\033[39m'
                pb = False
            if a == 39: # '
                out += '\\\''
            elif a == 92: # \
                out += '\\\\'
            else:
                out += chr(a)
        else:
            i += 1
            pb = True
            out += '\033[9%sm' % ((i % 2) + 1)
            t = table.get(a)
            if t:
                out += '\\%s' % t
            else:
                out += '\\x%02x' % a

    if pb:
        out += '\033[39m'
    out += "'"
    return out

def formatbytes(d):
    if isatty:
        return (highlight(d))
    else:
        return (ascii(d))

i = 0
isatty = sys.stdout.isatty()
if __name__ == '__main__':
    if len(sys.argv) not in (4, 5):
        exit('Usage %s host connectPort listenPort' % sys.argv[0]);

    interface = sys.argv[4] if len(sys.argv) == 5 else '127.0.0.1'
    reactor.listenTCP(int(sys.argv[3]), ServerFactory(), interface=interface)
    reactor.run()
