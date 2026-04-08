from client import Client
import ctypes
from ctypes import c_uint32, c_ubyte, POINTER, byref


path =  r"C:\Users\cpisa\Desktop\stream\DEVRASTA\NSPC\SWPG\SWAPPL\EXE\EXE1\fap1.ex1"
with open(path, "rb") as f:
        data = f.read()

if not data:
    raise ValueError("Empty file")

"""size = len(data)
buf = (c_ubyte * size).from_buffer_copy(data)

checksum = c_uint32(0)
err = c_uint32(0)"""

c = Client()

checksum_value = c.checksum(data)

print(f"Decimal checksum: {checksum_value}")
print(f"Hex checksum: 0x{checksum_value:08X}")