import ctypes
from ctypes import c_uint32, c_ubyte, POINTER, byref

import platform
print(f"ARCHITECTURE: {platform.architecture()}")

# Load the DLL
dll = ctypes.CDLL(r"C:\Users\cpisa\Desktop\Release\PEChecksumDll.dll")

# C signature:
# t_uint32 GetChecksumPE(t_uint8* pSrcPe, t_uint32 dimSrcPe,
#                        t_uint32* pChecksum, t_uint32* pCodErr)

dll.GetChecksumPE.argtypes = [
    POINTER(c_ubyte),   # pSrcPe
    c_uint32,           # dimSrcPe
    POINTER(c_uint32),  # pChecksum
    POINTER(c_uint32),  # pCodErr
]
dll.GetChecksumPE.restype = c_uint32


def get_pe_checksum(path: str) -> int:
    with open(path, "rb") as f:
        data = f.read()

    if not data:
        raise ValueError("Empty file")

    size = len(data)
    buf = (c_ubyte * size).from_buffer_copy(data)

    checksum = c_uint32(0)
    err = c_uint32(0)

    ok = dll.get_checksum(
        buf,
        c_uint32(size),
        byref(checksum),
        byref(err),
    )

    if ok == 0:
        raise RuntimeError(f"GetChecksumPE failed, error code={err.value}")

    return checksum.value




exe_path = r"C:\Users\cpisa\Desktop\stream\DEVRASTA\NSPC\SWPG\SWAPPL\EXE\EXE1\fap1.ex1"
chk = get_pe_checksum(exe_path)
print(f"Decimal checksum: {chk}")
print(f"Hex checksum: 0x{chk:08X}")