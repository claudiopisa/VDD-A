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

        # get checksum arguments and return type
        self.lib.get_checksum.argtypes = [
            POINTER(c_ubyte),   # pSrcPe
            c_uint32,           # dimSrcPe
            POINTER(c_uint32),  # pChecksum
            POINTER(c_uint32),  # pCodErr
        ]
        self.lib.get_checksum.restype = c_uint32

        # set checksum arguments and return type
        self.lib.set_checksum.argtypes = [
            POINTER(c_ubyte),
            c_uint32,
            c_uint32,
            POINTER(c_uint32),
        ]
        self.lib.set_checksum.restype = c_uint32

        # get timestamp arguments and return type
        self.lib.get_timestamp.argtypes = [
            POINTER(c_ubyte),
            c_uint32,
            POINTER(c_uint32),
            POINTER(c_uint32),
        ]

        # set timestamp arguments and return type
        self.lib.set_timestamp.argtypes = [
            POINTER(c_ubyte),
            c_uint32,
            c_uint32,
            POINTER(c_uint32),
        ]

        # verify checksum arguments and return type
        self.lib.verify_checksum.argtypes = [
            POINTER(c_ubyte),
            c_uint32,
            POINTER(c_uint32),
            POINTER(c_uint32),
            POINTER(c_uint32),
        ]
        self.lib.verify_checksum.restype = c_uint32

    def get_checksum(self, data: bytes):
        src_size = len(data)
        src = (c_ubyte * src_size).from_buffer_copy(data)

        checksum = c_uint32(0)
        err = c_uint32(0)

        res = self.lib.get_checksum(src, src_size, checksum, err)

        if res == 0:
            raise RuntimeError(f"GetChecksumPE failed, error code={err.value}")
        
        return checksum.value
    
    def set_checksum(self, data: bytes, new_checksum: c_uint32):
        src_size = len(data)
        src = (c_ubyte * src_size).from_buffer_copy(data)

        err = c_uint32(0)

        res = self.lib.set_checksum(src, src_size, new_checksum, err)

        if res == 0:
            raise RuntimeError(f"SetChecksumPE failed, error code={err.value}")

        return bytes(src)
    
    def get_timestamp(self, data: bytes):
        src_size = len(data)
        src = (c_ubyte * src_size).from_buffer_copy(data)
        timestamp = c_uint32(0)
        err = c_uint32(0)

        res = self.lib.get_timestamp(src, src_size, timestamp, err)

        if res == 0:
            raise RuntimeError(f"GetTimestampPE failed, error code={err.value}")

        return timestamp.value
    
    def set_timestamp(self, data: bytes, new_timestamp: c_uint32):
        src_size = len(data)
        src = (c_ubyte * src_size).from_buffer_copy(data)
        err = c_uint32(0)

        res = self.lib.set_timestamp(src, src_size, new_timestamp, err)

        if res == 0:
            raise RuntimeError(f"SetTimestampPE failed, error code={err.value}")

        return bytes(src)
    
    def verify_checksum(self, data: bytes):
        src_size = len(data)
        src = (c_ubyte * src_size).from_buffer_copy(data)

        calc_checksum = c_uint32(0) # calculated checksum
        file_checksum = c_uint32(0) # original checksum read from the file header
        err = c_uint32(0)

        res = self.lib.verify_checksum(src, src_size, file_checksum, calc_checksum, err)

        if res == 0:
            raise RuntimeError(f"VerifyChecksumPE failed, error code={err.value}")

        return {
            "calc_checksum": calc_checksum.value,
            "file_checksum": file_checksum.value,
            "match": calc_checksum.value == file_checksum.value,
        }
        

