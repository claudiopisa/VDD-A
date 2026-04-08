from client import Client
from pathlib import Path
import shutil


DLL_PATH = r"C:\Users\cpisa\Desktop\Release\PEChecksumDll.dll"
SRC_PATH = Path(r"C:\Users\cpisa\Desktop\stream\DEVRASTA\NSPC\SWPG\SWAPPL\EXE\EXE1\fap1.ex1")
DST_PATH = SRC_PATH.with_name(SRC_PATH.stem + "_copy" + SRC_PATH.suffix)

# Read the original file
with open(SRC_PATH, "rb") as f:
    src_data = f.read()

if not src_data:
    raise ValueError("Empty file")

c = Client(dll_path=DLL_PATH)

# Get the checksum
checksum_value = c.get_checksum(src_data)
print(f"Checksum header decimale: {checksum_value}")
print(f"Checksum header esadecimale: 0x{checksum_value:08X}")

# Check the original and calculated checksums
verify_info = c.verify_checksum(src_data)
print("Original verification:")
print(verify_info)

# Create a copy of the file
shutil.copy2(SRC_PATH, DST_PATH)

with open(DST_PATH, "rb") as f:
    copy_data = f.read()

# Set the checksum on the copy to zero
updated_data = c.set_checksum(copy_data, verify_info["calc_checksum"])
#updated_data = c.set_checksum(copy_data, 0)

# Rewrite the copy with the modified bytes
with open(DST_PATH, "wb") as f:
    f.write(updated_data)

# Read the updated copy
with open(DST_PATH, "rb") as f:
    final_data = f.read()

final_header_checksum = c.get_checksum(final_data)
final_verify_info = c.verify_checksum(final_data)

print(f"Copy header checksum: {final_header_checksum}")
print(f"Copy header checksum hex: 0x{final_header_checksum:08X}")

print("Updated copy verification:")
print(final_verify_info)
