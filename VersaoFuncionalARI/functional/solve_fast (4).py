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
    except Exception as e:
        print(f"[-] Erro no bloco {block_index}: {e}", file=sys.stderr)
        return block_index, b""

def main():
    if len(sys.argv) < 2:
        enc_file = "flag.txt.encrypted"
    else:
        enc_file = sys.argv[1]

    if not os.path.exists(enc_file):
        print(f"[-] Arquivo cifrado '{enc_file}' não encontrado.")
        sys.exit(1)

    workers = int(sys.argv[2]) if len(sys.argv) > 2 else os.cpu_count() or 4
    print(f"[+] Iniciando solver multiprocessado com {workers} trabalhadores...")

    with open(enc_file, "rb") as f:
        data = f.read()

    blocks = [data[i:i+60] for i in range(0, len(data), 60)]
    print(f"[+] Total de blocos a processar: {len(blocks)} ({len(data)} bytes)\n")

    # Provar a inversão em 1 bloco (Bloco Zero / Bloco #0)
    print("=" * 60)
    print("[+] PROVA DE CONCEITO: Decifrando e validando o Bloco #0...")
    print("=" * 60)
    block0_res = do_chunk(blocks[0])
    if block0_res and block0_res != b'[CHUNK FAILED TO DECRYPT]':
        print(f"[+] Sucesso! Bloco #0 decifrado ({len(block0_res)} bytes):")
        print(f"    Texto: {block0_res.decode('ascii', errors='replace')}")
    else:
        print(f"[-] Bloco #0 retorno: {block0_res}")
    print("=" * 60 + "\n")

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

    decrypted_data = b"".join([r for r in results if r and r != b'[CHUNK FAILED TO DECRYPT]'])
    
    os.makedirs("solution", exist_ok=True)
    out_file = "solution/flag.txt"
    with open(out_file, "wb") as f:
        f.write(decrypted_data)

    print(f"[+] Flag decifrada salva em: {out_file}")

if __name__ == "__main__":
    main()
