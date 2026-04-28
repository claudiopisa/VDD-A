from loadlib.client import Client
from pathlib import Path


class PEComparator:
    def __init__(self, lib_path: str | Path):
        # La classe ha una composizione stretta con Client MSL, che incapsula tutte le operazioni sui PE file
        self.client = Client(dll_path=lib_path)
        self.result = None

    def compare_pe_files(self, src1_path: Path, src2_path: Path) -> dict:
        """
        Confronta due file PE al netto di checksum e timestamp.

            dict con risultati del confronto:
            - 'identical': bool, True se identici
            - 'size_match': bool, True se stesse dimensioni
            - 'size1': int, dimensione file 1
            - 'size2': int, dimensione file 2
            - 'first_diff_offset': int o None, offset del primo byte differente
            - 'diff_bytes': list di (offset, byte1, byte2) per i primi 10 differenze
        """
        
        # Normalizza entrambi i file
        data1, diag1 = self._normalize_pe_file(src1_path)
        data2, diag2 = self._normalize_pe_file(src2_path)
        
        result = {
            'identical': data1 == data2, # Qui fa il confronto diretto byte a byteE, ma è possibile che due file con differenze minime (es. solo timestamp) risultino diversi. Per questo poi si fa un confronto più dettagliato.
            'size_match': len(data1) == len(data2),
            'size1': len(data1),
            'size2': len(data2),
            'first_diff_offset': None,
            'diff_bytes': [],
            'normalization': [diag1, diag2], # per la stampa a schermo delle info
        }
        
        # Salva stato interno della comparazione per stampe/riletture successive
        self.result = result

        # Se identici, finito
        if result['identical']:
            return self.result
        
        # Confronta byte a byte (per differenze effettive meglio controllare con un Hex Editor)
        min_len = min(len(data1), len(data2))
        for offset in range(min_len):
            if data1[offset] != data2[offset]:
                if result['first_diff_offset'] is None:
                    result['first_diff_offset'] = offset
                
                # Raccolti i primi 10 differenze
                if len(result['diff_bytes']) < 10: # aggiustare a piacere
                    result['diff_bytes'].append({
                        'offset': offset,
                        'byte1': data1[offset],
                        'byte2': data2[offset],
                        'hex1': f"0x{data1[offset]:02X}",
                        'hex2': f"0x{data2[offset]:02X}",
                    })
        
        # aggiorna (ridondante ma messo per chiarezza)
        self.result = result

        return self.result

    def _normalize_pe_file(self, pe_path: Path) -> tuple[bytes, dict]:

        with open(pe_path, "rb") as f:
            data = f.read()
        
        # Stato iniziale
        before_checksum = self.client.get_checksum(data)
        before_timestamp = self.client.get_timestamp(data)

        # Azzera checksum e timestamp
        data = self.client.set_checksum(data, 0)
        
        # Azzera timestamp
        data = self.client.set_timestamp(data, 0)
        
        # Stato finale dopo normalizzazione
        after_checksum = self.client.get_checksum(data)
        after_timestamp = self.client.get_timestamp(data)

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

    def print_comparison(self):
        if self.result is None:
            raise RuntimeError("Nessun risultato disponibile: eseguire prima compare_pe_files().")
        print("=" * 70)
        print("CONFRONTO PE FILES (al netto di checksum e timestamp)")
        print("=" * 70)
        
        print(f"\nSize file 1: {self.result['size1']:,} bytes")
        print(f"Size file 2: {self.result['size2']:,} bytes")
        print(f"Dimensioni corrispondono: {self.result['size_match']}")

        print("\nDettagli normalizzazione (prima/dopo):")
        for idx, info in enumerate(self.result["normalization"], start=1):
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
        
        if self.result['identical']:
            print("\nI file sono IDENTICI")
        else:
            print("\nI file DIFFERISCONO")
            print(f"  Primo byte differente a offset: {self.result['first_diff_offset']:,} (0x{self.result['first_diff_offset']:X})")
            print(f"\n  Primi {len(self.result['diff_bytes'])} byte differenti:")
            print(f"  {'Offset':<12} {'File1':<15} {'File2':<15}")
            print(f"  {'-' * 12} {'-' * 15} {'-' * 15}")
            for diff in self.result['diff_bytes']:
                print(f"  {diff['offset']:<12,} {diff['hex1']:<15} {diff['hex2']:<15}")


if __name__ == "__main__":
    # test
    DLL_PATH = Path(__file__).resolve().parents[2] / "resource" / "pechecksum" / "PEChecksum" / "PEChecksumDll.dll"
    SRC1_PATH = Path(r"C:\Users\cpisa\Desktop\exodia_eulynx\NSPC\SWADA\EXE\EXE1\adat1_orig.exe")
    SRC2_PATH = Path(r"C:\Users\cpisa\Desktop\exodia_eulynx\NSPC\SWADA\EXE\EXE1\adat1.exe")

    comparator = PEComparator(DLL_PATH)
    comparator.compare_pe_files(SRC1_PATH, SRC2_PATH)
    comparator.print_comparison()
