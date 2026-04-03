from msl.loadlib import Client64
from pathlib import Path
import ctypes
from ctypes import c_uint32, c_ubyte, POINTER, byref

class Client(Client64):
    def __init__(self, dll_path : str | Path, dll_type : str = "windll"):
        
        if isinstance(dll_path, str):
            self.filepath = Path(dll_path)
        else:
            self.filepath = dll_path

        #dll_type must be 'windll' or 'cdll'
        if dll_type in ('windll', 'cdll'):
            self.dll_type = dll_type
        else:
            raise ValueError("dll_type must be 'windll' or 'cdll'")

        server_kwargs = {
            "dll_path": str(self.filepath),
            "dll_type": self.dll_type,
        }

        super(Client, self).__init__(module32='server.py', **server_kwargs)
        
    def get_checksum(self, data):
        return self.request32('get_checksum', data)
    
    def set_checksum(self, data, new_checksum):
        return self.request32('set_checksum', data, int(new_checksum))
    
    def verify_checksum(self, data):
        return self.request32('verify_checksum', data)