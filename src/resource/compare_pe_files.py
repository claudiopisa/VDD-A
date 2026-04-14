from client import Client
from pathlib import Path


def normalize_pe_file(client: Client, pe_path: Path) -> tuple[bytes, dict]:
    """
    Legge un file PE, azzera checksum e timestamp, e ritorna i dati modificati
    con una diagnostica prima/dopo.
    """
    with open(pe_path, "rb") as f:
        data = f.read()
    
    # Stato iniziale
    before_checksum = client.get_checksum(data)
    before_timestamp = client.get_timestamp(data)

    # Azzera checksum e timestamp
    data = client.set_checksum(data, 0)
    
    # Azzera timestamp
    data = client.set_timestamp(data, 0)
    
    # Stato finale dopo normalizzazione
    after_checksum = client.get_checksum(data)
    after_timestamp = client.get_timestamp(data)

    diagnostics = {
        "path": str(pe_path),
        "before": {
            "header_checksum": before_checksum,
            "timestamp": before_timestamp,
        },
        "after": {
            "header_checksum": after_checksum,
            "timestamp": after_timestamp,
        },
    }

    return data, diagnostics


def compare_pe_files(dll_path: str | Path, src1_path: Path, src2_path: Path) -> dict:
    """
    Confronta due file PE al netto di checksum e timestamp.
    
    Args:
        dll_path: Path al DLL di checksum/timestamp
        src1_path: Path al primo PE file
        src2_path: Path al secondo PE file
    
    Returns:
        dict con risultati del confronto:
        - 'identical': bool, True se identici
        - 'size_match': bool, True se stesse dimensioni
        - 'size1': int, dimensione file 1
        - 'size2': int, dimensione file 2
        - 'first_diff_offset': int o None, offset del primo byte differente
        - 'diff_bytes': list di (offset, byte1, byte2) per i primi 10 differenze
    """
    
    client = Client(dll_path=dll_path)
    
    # Normalizza entrambi i file
    data1, diag1 = normalize_pe_file(client, src1_path)
    data2, diag2 = normalize_pe_file(client, src2_path)
    
    result = {
        'identical': data1 == data2,
        'size_match': len(data1) == len(data2),
        'size1': len(data1),
        'size2': len(data2),
        'first_diff_offset': None,
        'diff_bytes': [],
        'normalization': [diag1, diag2],
    }
    
    # Se identici, finito
    if result['identical']:
        return result
    
    # Confronta byte a byte
    min_len = min(len(data1), len(data2))
    for offset in range(min_len):
        if data1[offset] != data2[offset]:
            if result['first_diff_offset'] is None:
                result['first_diff_offset'] = offset
            
            # Raccolti i primi 10 differenze
            if len(result['diff_bytes']) < 10:
                result['diff_bytes'].append({
                    'offset': offset,
                    'byte1': data1[offset],
                    'byte2': data2[offset],
                    'hex1': f"0x{data1[offset]:02X}",
                    'hex2': f"0x{data2[offset]:02X}",
                })
    
    return result


def print_comparison(result: dict):
    """Stampa i risultati del confronto in modo leggibile."""
    print("=" * 70)
    print("CONFRONTO PE FILES (al netto di checksum e timestamp)")
    print("=" * 70)
    
    print(f"\nSize file 1: {result['size1']:,} bytes")
    print(f"Size file 2: {result['size2']:,} bytes")
    print(f"Dimensioni corrispondono: {result['size_match']}")

    print("\nDettagli normalizzazione (prima/dopo):")
    for idx, info in enumerate(result["normalization"], start=1):
        print(f"\n  File {idx}: {info['path']}")
        print(
            f"    Prima -> checksum(header): {info['before']['header_checksum']} "
            f"(0x{info['before']['header_checksum']:08X}), "
            f"timestamp: {info['before']['timestamp']} "
            f"(0x{info['before']['timestamp']:08X})"
        )
        print(
            f"    Dopo  -> checksum(header): {info['after']['header_checksum']} "
            f"(0x{info['after']['header_checksum']:08X}), "
            f"timestamp: {info['after']['timestamp']} "
            f"(0x{info['after']['timestamp']:08X})"
        )
    
    if result['identical']:
        print("\nI file sono IDENTICI")
    else:
        print("\nI file DIFFERISCONO")
        print(f"  Primo byte differente a offset: {result['first_diff_offset']:,} (0x{result['first_diff_offset']:X})")
        print(f"\n  Primi {len(result['diff_bytes'])} byte differenti:")
        print(f"  {'Offset':<12} {'File1':<15} {'File2':<15}")
        print(f"  {'-' * 12} {'-' * 15} {'-' * 15}")
        for diff in result['diff_bytes']:
            print(f"  {diff['offset']:<12,} {diff['hex1']:<15} {diff['hex2']:<15}")


# Configurazione
DLL_PATH = r"C:\Users\cpisa\Desktop\Release\PEChecksumDll.dll"
SRC1_PATH = Path(r"C:\Users\cpisa\Desktop\stream\DEVRASTA\NSPC\SWPG\SWAPPL\EXE\EXE1\fap1.ex1")
#SRC2_PATH = Path(r"C:\Users\cpisa\Desktop\stream\DEVRASTA\NSPC\SWPG\SWAPPL\EXE\EXE1\fap1.ex1")
SRC2_PATH = Path(r"C:\Users\cpisa\Desktop\stream\DEVRASTA\NSPC\SWPG\SWAPPL\EXE\EXE2\fap1.ex2")

    
# Confronta
result = compare_pe_files(DLL_PATH, SRC1_PATH, SRC2_PATH)
    
# Stampa risultati
print_comparison(result)
