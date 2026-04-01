from msl.loadlib import Server32
import ctypes
from ctypes import c_uint32, c_ubyte, POINTER, byref


class Server(Server32):

    def __init__(self, host, port, **kwargs):
        #extract the path to the DLL from kwargs, or use a default path
        dll_path = kwargs.get("dll_path", " ")

        if not dll_path:
            raise ValueError("DLL path must be provided in kwargs with key 'dll_path'")
        
        dll_type = kwargs.get("dll_type", "windll")
        
        #super().__init__("C:\\Users\\cpisa\\Desktop\\Release\\PEChecksumDll.dll", "windll", host, port)
        super().__init__(dll_path, dll_type, host, port)

        #self.version = self.lib.version()

    def get_checksum(self, data):
        #return self.lib.get_checksum(buf, size, checksum_ref, err_ref)

        self.lib.get_checksum.argtypes = [
            POINTER(c_ubyte),   # pSrcPe
            c_uint32,           # dimSrcPe
            POINTER(c_uint32),  # pChecksum
            POINTER(c_uint32),  # pCodErr
        ]
        self.lib.get_checksum.restype = c_uint32

        #with open(path, "rb") as f:
        #    data = f.read()

        #if not data:
        #    raise ValueError("File vuoto")

        size = len(data)
        buf = (c_ubyte * size).from_buffer_copy(data)

        checksum = c_uint32(0)
        err = c_uint32(0)

        res = self.lib.get_checksum(buf, size, checksum, err)

        if res == 0:
            raise RuntimeError(f"GetChecksumPE fallita, codice errore={err.value}")
        
        return checksum.value
    
    def set_checksum(self, data, new_checksum):
        self.lib.set_checksum.argtypes = [
            POINTER(c_ubyte),
            c_uint32,
            c_uint32,
            POINTER(c_uint32),
        ]
        self.lib.set_checksum.restype = c_uint32

        size = len(data)
        buf = (c_ubyte * size).from_buffer_copy(data)

        err = c_uint32(0)

        res = self.lib.set_checksum(buf, size, new_checksum, err)

        if res == 0:
            raise RuntimeError(f"SetChecksumPE fallita, codice errore={err.value}")

        #return bytes(buf)
        

