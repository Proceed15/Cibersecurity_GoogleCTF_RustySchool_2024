import os
import sys
import hashlib
import struct
from sage.all import *

# Primo P de 96 bits do desafio
P = 79160129948973046149879599747

def p16(x):
    return struct.pack("<H", x)

def u16(x):
    return struct.unpack("<H", x)[0]

def xor(a: bytes, b: bytes) -> bytes:
    assert len(a) == len(b)
    return bytes([x ^ y for x, y in zip(a, b)])

def derive(seed: bytes, *, m: int) -> bytes:
    assert len(seed) == 12
    arr = [u16(seed[i * 2 : i * 2 + 2]) for i in range(6)]
    out = []
    for i in range(6):
        key = 0
        c0, c1 = arr[(i + 2 * m) % 6], arr[(i + 2 * m + 1) % 6]
        while c0 and c1:
            key ^= c0 & -(c1 & 1)
            v17 = (c0 << 1) ^ 0x2B
            if (c0 & 0x8000) == 0:
                v17 = c0 << 1
            c0 = v17 & 0xFFFF
            c1 >>= 1
        out.append(arr[(i + 4 + m) % 6] ^ key)
    return b"".join(p16(x) for x in out)

# Inicialização do corpo finito GF(2^16) com polinômio redutor 0x2B (x^16 + x^5 + x^3 + x + 1)
R = PolynomialRing(GF(2), names=('x',))
(x,) = R._first_ngens(1)
irreducible_poly = x**16 + x**5 + x**3 + x + 1
F = GF(2**16, modulus=irreducible_poly, name='a')

def solve_(solve_for, m):
    F_solve_for = [F.from_integer(int(val)) for val in solve_for]

    G = PolynomialRing(F, names=('a0', 'a1', 'a2', 'a3', 'a4', 'a5'))
    a0, a1, a2, a3, a4, a5 = G.gens()

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

    my_id = Ideal(eqs)
    if my_id.dimension() != 0:
        return []

    my_variety = my_id.variety()
    solutions = [[
        variety[a0].to_integer(),
        variety[a1].to_integer(),
        variety[a2].to_integer(),
        variety[a3].to_integer(),
        variety[a4].to_integer(),
        variety[a5].to_integer()
    ] for variety in my_variety]
    return solutions

def solve2_(rv0, rv1):
    rv0_f = [F.from_integer(int(val)) for val in rv0]
    rv1_f = [F.from_integer(int(val)) for val in rv1]

    G = PolynomialRing(F, names=('a0', 'a1', 'a2', 'a3', 'a4', 'a5'))
    a0, a1, a2, a3, a4, a5 = G.gens()

    eqs = [
        a0 * a1 + a4 - rv0_f[0],
        a1 * a2 + a5 - rv0_f[1],
        a2 * a3 + a0 - rv0_f[2],
        a3 * a4 + a1 - rv0_f[3],
        a4 * a5 + a2 - rv0_f[4],
        a5 * a0 + a3 - rv0_f[5],
        a2 * a3 + a5 - rv1_f[0],
        a3 * a4 + a0 - rv1_f[1],
        a4 * a5 + a1 - rv1_f[2],
        a5 * a0 + a2 - rv1_f[3],
        a0 * a1 + a3 - rv1_f[4],
        a1 * a2 + a4 - rv1_f[5],
    ]

    my_id = Ideal(eqs)
    if my_id.dimension() != 0:
        return []

    my_variety = my_id.variety()
    solutions = [[
        variety[a0].to_integer(),
        variety[a1].to_integer(),
        variety[a2].to_integer(),
        variety[a3].to_integer(),
        variety[a4].to_integer(),
        variety[a5].to_integer()
    ] for variety in my_variety]
    return solutions

def solve(rv, m):
    possible_solution = solve_([u16(rv[i * 2 : i * 2 + 2]) for i in range(6)], m)
    return [b"".join(p16(x) for x in y) for y in possible_solution]

def solve2(rv0, rv1):
    possible_solution = solve2_([u16(rv0[i * 2 : i * 2 + 2]) for i in range(6)], [u16(rv1[i * 2 : i * 2 + 2]) for i in range(6)])
    return [b"".join(p16(x) for x in y) for y in possible_solution]

def to_int(x):
    return int.from_bytes(x, "little")

N_ROUNDS = 12

def do_one_round(output, rv0, rv1, n):
    shits = []
    b2, cb1, bs, cb2 = output[:12], output[12:24], output[24:36], output[36:48]
    b1 = xor(cb2, hashlib.sha1(rv1 + b2).digest()[:12])
    b0 = xor(cb1, hashlib.md5(rv0 + b2).digest()[:12])
    b3 = (((((to_int(bs) - pow(to_int(b2), to_int(b1), P) + P) % P) * pow(to_int(b0), -1, P)) % P - to_int(b1) + P) % P).to_bytes(12, "little")

    for OLD_rv0 in solve2(rv0, rv1):
        if n == N_ROUNDS - 1:
            return [(b"".join([b0, b1, b2, b3]), OLD_rv0, b'', n + 1)]
        for OLDEST_rv0 in solve(OLD_rv0, m=0):
            OLD_rv1 = derive(OLDEST_rv0, m=1)
            shits.append((b"".join([b0, b1, b2, b3]), OLD_rv0, OLD_rv1))
    return shits

def decrypt_block(output):
    assert len(output) == 60
    POSSIBLE_OUTPUTS = []
    rv1 = output[48:60]
    for pot_old_rv0 in solve(rv1, m=1):
        POSSIBLE_OUTPUTS.append((output[:48], derive(pot_old_rv0, m=0), rv1))

    for n in range(N_ROUNDS):
        POSSIBLE_OLD_INPUTS = []
        for out_data, rv0_cur, rv1_cur in POSSIBLE_OUTPUTS:
            POSSIBLE_OLD_INPUTS.extend(do_one_round(out_data, rv0_cur, rv1_cur, n))

        POSSIBLE_OLD_INPUTS = list(set(POSSIBLE_OLD_INPUTS))
        POSSIBLE_OUTPUTS = POSSIBLE_OLD_INPUTS

    for orig_input, _, _, _ in POSSIBLE_OLD_INPUTS:
        if all((c >= 0x20 and c < 0x7f) or c in [0xa, 0xd] for c in orig_input):
            return orig_input
    return b'[CHUNK FAILED TO DECRYPT]'

def main():
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
