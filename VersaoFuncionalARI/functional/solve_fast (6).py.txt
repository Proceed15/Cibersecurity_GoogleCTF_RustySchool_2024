#!/usr/bin/env python3
import sys
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_single_block(block_hex, idx):
    from solve import decrypt_block
    block_bytes = bytes.fromhex(block_hex)
    res = decrypt_block(block_bytes)
    return idx, res

def main():
    enc_file = sys.argv[1] if len(sys.argv) > 1 else "flag.txt.encrypted"

    if not os.path.exists(enc_file):
        print(f"[-] Arquivo cifrado '{enc_file}' não foi encontrado.")
        sys.exit(1)

    workers = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count() or 4
    print(f"[+] Iniciando solver multiprocessado com {workers} trabalhadores...")

    with open(enc_file, "rb") as f:
        data = f.read()

    blocks = [data[i:i+60] for i in range(0, len(data), 60)]
    print(f"[+] Total de blocos a processar: {len(blocks)} ({len(data)} bytes)\n")

    # ============================================================
    # FASE 0: PROVA DE CONCEITO (Decifrando e validando o Bloco #0)
    # ============================================================
    print("=" * 60)
    print("[+] PROVA DE CONCEITO: Decifrando e validando o Bloco #0...")
    print("=" * 60)
    from solve import decrypt_block
    block0_dec = decrypt_block(blocks[0])
    try:
        text0 = block0_dec.decode('ascii', errors='replace')
    except Exception:
        text0 = str(block0_dec)
    print(f"[+] Sucesso! Bloco #0 decifrado ({len(block0_dec)} bytes):")
    print(f"    Texto: {text0}")
    print("=" * 60 + "\n")

    start_time = time.time()
    results = [None] * len(blocks)

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(process_single_block, block.hex(), idx): idx
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
    
    # Salva na pasta solution/ se ela existir, ou no diretório corrente
    out_dir = "solution" if os.path.exists("solution") else "."
    out_file = os.path.join(out_dir, "flag.txt")
    
    with open(out_file, "wb") as f:
        f.write(decrypted_data)

    print(f"[+] Flag decifrada salva em: {out_file}")

if __name__ == "__main__":
    main()
