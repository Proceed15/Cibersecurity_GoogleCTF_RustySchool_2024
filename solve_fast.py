#!/usr/bin/env python3
"""
solve_fast.py - Decifrador Multiprocessado para Rusty School (Google CTF 2024)
Executa a resolução dos sistemas polinomiais no SageMath em paralelo entre múltiplos núcleos de CPU.
"""

import sys
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_single_block_sage(block_data_hex, block_index):
    """
    Subprocesso que invoca o SageMath para resolver individualmente cada bloco de 60 bytes.
    """
    cmd = f'sage -c "from solve import decrypt_block; print(decrypt_block(bytes.fromhex(\'{block_data_hex}\')).hex())"'
    pipe = os.popen(cmd)
    res_hex = pipe.read().strip()
    pipe.close()
    
    return block_index, bytes.fromhex(res_hex) if res_hex else b""

def main():
    if len(sys.argv) < 2:
        enc_file = "flag.txt.encrypted"
    else:
        enc_file = sys.argv[1]

    if not os.path.exists(enc_file):
        print(f"[-] Arquivo cifrado '{enc_file}' não foi encontrado.")
        print("    Exemplo de uso: python3 solve_fast.py flag.txt.encrypted [num_workers]")
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
            executor.submit(process_single_block_sage, block.hex(), idx): idx
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
    out_file = enc_file + ".fast.dec.txt"
    with open(out_file, "wb") as f:
        f.write(decrypted_data)

    print(f"[+] Flag decifrada salva em: {out_file}")

if __name__ == "__main__":
    main()
