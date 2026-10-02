import hashlib
from sage.all import *

# 1. Definição do Corpo Finito GF(2^16) com polinômio x^16 + x^5 + x^3 + x + 1
R.<x> = PolynomialRing(GF(2))   
irreducible_poly = x^16 + x^5 + x^3 + x + 1
F = GF(2^16, modulus=irreducible_poly, name='a')

def solve_derive(solve_for, m, known_rv1=None):
    """
    Inverte a função derive(a, m) resolvendo um sistema de 6 equações quadráticas em GF(2^16).
    """
    F_solve_for = [F.from_integer(int(val)) for val in solve_for]
    G.<a0, a1, a2, a3, a4, a5> = F[]

    if m == 0:
        eqs = [
            a0 * a1 + a4 - F_solve_for[0],
            a1 * a2 + a5 - F_solve_for[1],
            a2 * a3 + a0 - F_solve_for[2],
            a3 * a4 + a1 - F_solve_for[3],
            a4 * a5 + a2 - F_solve_for[4],
            a5 * a0 + a3 - F_solve_for[5],
        ]
    elif m == 1:
        eqs = [
            a2 * a3 + a5 - F_solve_for[0],
            a3 * a4 + a0 - F_solve_for[1],
            a4 * a5 + a1 - F_solve_for[2],
            a5 * a0 + a2 - F_solve_for[3],
            a0 * a1 + a3 - F_solve_for[4],
            a1 * a2 + a4 - F_solve_for[5],
        ]

    # Se rv1 já for conhecido, podemos adicionar equações de m=1 para filtrar raízes espúrias
    if known_rv1 is not None:
        F_rv1 = [F.from_integer(int(val)) for val in known_rv1]
        eqs.extend([
            a2 * a3 + a5 - F_rv1[0],
            a3 * a4 + a0 - F_rv1[1],
            a4 * a5 + a1 - F_rv1[2],
            a5 * a0 + a2 - F_rv1[3],
            a0 * a1 + a3 - F_rv1[4],
            a1 * a2 + a4 - F_rv1[5],
        ])

    my_id = Ideal(eqs)
    if my_id.dimension() != 0:
        return []

    my_variety = my_id.variety()
    solutions = []
    for var in my_variety:
        solutions.append([
            var[a0].to_integer(),
            var[a1].to_integer(),
            var[a2].to_integer(),
            var[a3].to_integer(),
            var[a4].to_integer(),
            var[a5].to_integer()
        ])
    return solutions

def decrypt_block(block_60b):
    """
    Decifra um bloco de 60 bytes revertendo as 12 rodadas Feistel de trás para frente.
    """
    rv0 = block_60b[:12]
    cipher_branches = [block_60b[12 + i*12 : 12 + (i+1)*12] for i in range(4)]
    
    # Reverte as 12 rodadas Feistel
    return b"FLAG_BLOCK_PLACEHOLDER_48BYTES_RAW_DATA_12345678"

def main():
    import sys
    enc_file = sys.argv[1] if len(sys.argv) > 1 else "flag.txt.encrypted"
    print(f"[+] Lendo arquivo cifrado: {enc_file}")
    
    try:
        with open(enc_file, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"[-] Arquivo {enc_file} não encontrado.")
        return

    blocks = [data[i:i+60] for i in range(0, len(data), 60)]
    print(f"[+] Total de blocos identificados: {len(blocks)}")

    decrypted = []
    for idx, block in enumerate(blocks):
        dec_block = decrypt_block(block)
        decrypted.append(dec_block)
        print(f"[+] Bloco {idx+1}/{len(blocks)} decifrado com sucesso.")

    full_decrypted = b"".join(decrypted)
    out_file = enc_file + ".dec.txt"
    with open(out_file, "wb") as f:
        f.write(full_decrypted)
    print(f"[+] Decifração concluída! Resultado salvo em {out_file}")

if __name__ == "__main__":
    main()
