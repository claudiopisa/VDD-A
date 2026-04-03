from client import Client
from pathlib import Path
import shutil


DLL_PATH = r"C:\Users\cpisa\Desktop\Release\PEChecksumDll.dll"
SRC_PATH = Path(r"C:\Users\cpisa\Desktop\stream\DEVRASTA\NSPC\SWPG\SWAPPL\EXE\EXE1\fap1.ex1")
DST_PATH = SRC_PATH.with_name(SRC_PATH.stem + "_copy" + SRC_PATH.suffix)

# leggi il file originale
with open(SRC_PATH, "rb") as f:
    src_data = f.read()

if not src_data:
    raise ValueError("File vuoto")

c = Client(dll_path=DLL_PATH)

# prende checksum
checksum_value = c.get_checksum(src_data)
print(f"Checksum header decimale: {checksum_value}")
print(f"Checksum header esadecimale: 0x{checksum_value:08X}")

# verifico checksum originale e calcolato
verify_info = c.verify_checksum(src_data)
print("Verify originale:")
print(verify_info)

#  creo una copia del file
shutil.copy2(SRC_PATH, DST_PATH)

with open(DST_PATH, "rb") as f:
    copy_data = f.read()

# imposto sulla copia il checksum a zero
updated_data = c.set_checksum(copy_data, verify_info["calc_checksum"])
#updated_data = c.set_checksum(copy_data, 0)

# riscrivo la copia con i bytes modificati
with open(DST_PATH, "wb") as f:
    f.write(updated_data)

# leggi  copia aggiornata
with open(DST_PATH, "rb") as f:
    final_data = f.read()

final_header_checksum = c.get_checksum(final_data)
final_verify_info = c.verify_checksum(final_data)

print(f"Checksum header copia: {final_header_checksum}")
print(f"Checksum header copia hex: 0x{final_header_checksum:08X}")

print("Verify copia aggiornata:")
print(final_verify_info)
