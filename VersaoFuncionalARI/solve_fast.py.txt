#!/usr/bin/env python3
import sys
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, '.')
from solve import do_chunk

def process_block(block_data, block_index):
    try:
        decrypted_bytes = do_chunk(block_data)
        return block_index, decrypted_bytes
    except Exception:
        return block_index, b""

def main():
    enc_file = sys.argv[1] if len(sys.argv) > 1 else "flag.txt.encrypted"

    if not os.path.exists(enc_file):
        print(f"[-] Arquivo cifrado '{enc_file}' não encontrado.")
        sys.exit(1)

    workers = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count() or 4
    print(f"[+] Iniciando solver multiprocessado com {workers} trabalhadores...")

    with open(enc_file, "rb") as f:
        data = f.read()

    blocks = [data[i:i+60] for i in range(0, len(data), 60)]
    print(f"[+] Total de blocos a processar: {len(blocks)} ({len(data)} bytes)")

    start_time = time.time()
    results = [None] * len(blocks)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_block, block, idx): idx
            for idx, block in enumerate(blocks)
        }

        completed = 0
        for future in as_completed(futures):
            idx, dec_bytes = future.result()
            results[idx] = dec_bytes
            completed += 1
            print(f"\r[+] Progresso: {completed}/{len(blocks)} blocos decifrados ({completed/len(blocks)*100:.1f}%)", end="")

    print("\n[+] Todos os blocos foram processados!")
    elapsed = time.time() - start_time
    print(f"[+] Tempo total de execução: {elapsed:.2f} segundos")

    decrypted_data = b"".join(filter(None, results))
    out_file = "solution/flag.txt" if os.path.exists("solution") else "flag.txt.dec.txt"
    with open(out_file, "wb") as f:
        f.write(decrypted_data)

    print(f"[+] Flag decifrada salva em: {out_file}")

if __name__ == "__main__":
    main()