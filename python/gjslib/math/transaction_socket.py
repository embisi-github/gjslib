#!/usr/bin/env python
#a Documentation
"""
"""

#a Imports
import socket
import errno
import struct
import pickle

#a Socket class
#c c_transaction_socket
class c_transaction_socket( object ):
    def __init__( self, skt ):
        self.skt = skt
        self.skt.settimeout(0)
        self.rx_buffer = ""
        pass
    def is_alive( self ):
        return self.skt is not None
    def close( self ):
        if self.skt is not None:
            try:
                self.skt.close()
                pass
            except:
                pass
            self.skt = None
            pass
        pass
    def poll_data( self ):
        pkt = self.parse_rx_buffer()
        while pkt is None:
            if self.skt is None:
                return None
            try:
                data = self.skt.recv(4096)
            except socket.timeout, e:
                return None
            except socket.error, e:
                if e.errno==errno.EAGAIN:
                    return None
                self.close()
                return None
            else:
                if len(data) == 0:
                    self.close()
                    return None
                pass
            pkt = self.parse_rx_buffer(data)
            pass
        return pkt
    def parse_rx_buffer( self, new_data=None ):
        if new_data is not None:
            self.rx_buffer += new_data
            pass
        if not self.can_unpack_rx_buffer():
            return None
        return self.unpack_rx_buffer()
    def send_data( self, data ):
        pkt = self.pack_tx_data( data )
        if self.skt is not None:
            try:
                self.skt.sendall(pkt)
                pass
            except:
                self.close()
                pass
        pass
    def pack_tx_data( self, data ):
        body = pickle.dumps(data)
        l = len(body)
        hdr = struct.pack("<h",l)
        return hdr+body
    def can_unpack_rx_buffer( self ):
        l = len(self.rx_buffer)
        if l<2: return False
        body_len = struct.unpack("<h",self.rx_buffer[:2])[0]
        if l<body_len+2: return False
        return True
    def unpack_rx_buffer( self ):
        body_len = struct.unpack("<h",self.rx_buffer[:2])[0]
        d = self.rx_buffer[2:body_len+2]
        self.rx_buffer = self.rx_buffer[2+body_len:]
        return pickle.loads(d)


