import sys
import hashlib
from sage.all import *

# 1. Definição do Corpo Finito GF(2^16) com o polinômio x^16 + x^5 + x^3 + x + 1 (0x2B)
R = PolynomialRing(GF(2), names=('x',))
(x,) = R._first_ngens(1)
irreducible_poly = x**16 + x**5 + x**3 + x + 1
F = GF(2**16, modulus=irreducible_poly, name='a')

# Primo P de 96 bits (12 bytes)
P = 79160129948973046149879599747

def u16(b):
    return int.from_bytes(b, 'little')

def p16(val):
    return (int(val) & 0xFFFF).to_bytes(2, 'little')

def xor_bytes(b1, b2):
    return bytes(x ^ y for x, y in zip(b1, b2))

def solve_(solve_for, m):
    """
    Resolve o sistema de 6 equações quadráticas em GF(2^16) para encontrar candidatos a rv0/rv1.
    Compatível com SageMath 10+ (from_integer e to_integer).
    """
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
    else:
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

    solutions = []
    for var in my_id.variety():
        solutions.append([
            var[a0].to_integer(),
            var[a1].to_integer(),
            var[a2].to_integer(),
            var[a3].to_integer(),
            var[a4].to_integer(),
            var[a5].to_integer()
        ])
    return solutions

def solve2_(rv0, rv1):
    """
    Resolve o sistema estendido (12 equações) em GF(2^16) para filtrar raízes espúrias.
    """
    F_rv0 = [F.from_integer(int(val)) for val in rv0]
    F_rv1 = [F.from_integer(int(val)) for val in rv1]
    G = PolynomialRing(F, names=('a0', 'a1', 'a2', 'a3', 'a4', 'a5'))
    a0, a1, a2, a3, a4, a5 = G.gens()

    eqs = [
        a0 * a1 + a4 - F_rv0[0],
        a1 * a2 + a5 - F_rv0[1],
        a2 * a3 + a0 - F_rv0[2],
        a3 * a4 + a1 - F_rv0[3],
        a4 * a5 + a2 - F_rv0[4],
        a5 * a0 + a3 - F_rv0[5],
        a2 * a3 + a5 - F_rv1[0],
        a3 * a4 + a0 - F_rv1[1],
        a4 * a5 + a1 - F_rv1[2],
        a5 * a0 + a2 - F_rv1[3],
        a0 * a1 + a3 - F_rv1[4],
        a1 * a2 + a4 - F_rv1[5],
    ]

    my_id = Ideal(eqs)
    if my_id.dimension() != 0:
        return []

    solutions = []
    for var in my_id.variety():
        solutions.append([
            var[a0].to_integer(),
            var[a1].to_integer(),
            var[a2].to_integer(),
            var[a3].to_integer(),
            var[a4].to_integer(),
            var[a5].to_integer()
        ])
    return solutions

def do_one_round(b2, cb1, bs, cb2, rv0_bytes, rv1_bytes):
    """
    Inverte uma única rodada da Cifra Feistel de 4 ramos.
    """
    b1 = xor_bytes(cb2, hashlib.sha1(rv1_bytes + b2).digest()[:12])
    b0 = xor_bytes(cb1, hashlib.md5(rv0_bytes + b2).digest()[:12])
    
    i0 = int.from_bytes(b0, 'little')
    i1 = int.from_bytes(b1, 'little')
    i2 = int.from_bytes(b2, 'little')
    bs_val = int.from_bytes(bs, 'little')
    
    term1 = (bs_val - pow(i2, i1, P)) % P
    inv_i0 = pow(i0, -1, P)
    i3 = (term1 * inv_i0 - i1) % P
    b3 = (int(i3) % P).to_bytes(12, 'little')

    rv0_u16 = [u16(rv0_bytes[i*2 : i*2+2]) for i in range(6)]
    rv1_u16 = [u16(rv1_bytes[i*2 : i*2+2]) for i in range(6)]
    
    prev_rv0_candidates = solve2_(rv0_u16, rv1_u16)
    
    results = []
    for cand in prev_rv0_candidates:
        prev_rv0_bytes = b"".join(p16(x) for x in cand)
        results.append((b0, b1, b2, b3, prev_rv0_bytes))
        
    return results

def do_chunk(chunk_60b):
    """
    Inverte as 12 rodadas para um bloco de 60 bytes (48 bytes ciphertext + 12 bytes rv1).
    """
    if len(chunk_60b) < 60:
        return b""

    cipher = chunk_60b[:48]
    rv1_last = chunk_60b[48:60]
    
    b2 = cipher[0:12]
    cb1 = cipher[12:24]
    bs = cipher[24:36]
    cb2 = cipher[36:48]
    
    rv1_last_u16 = [u16(rv1_last[i*2 : i*2+2]) for i in range(6)]
    candidates_rv0 = solve_(rv1_last_u16, m=1)
    
    if not candidates_rv0:
        return b""
        
    for cand in candidates_rv0:
        rv0_bytes = b"".join(p16(x) for x in cand)
        rv1_bytes = rv1_last
        
        curr_branches = [(b2, cb1, bs, cb2, rv0_bytes, rv1_bytes)]
        
        for round_idx in range(12):
            next_branches = []
            for (curr_b2, curr_cb1, curr_bs, curr_cb2, c_rv0, c_rv1) in curr_branches:
                prev_list = do_one_round(curr_b2, curr_cb1, curr_bs, curr_cb2, c_rv0, c_rv1)
                for (prev_b0, prev_b1, prev_b2, prev_b3, prev_rv0) in prev_list:
                    next_branches.append((prev_b0, prev_b1, prev_b2, prev_b3, prev_rv0, c_rv0))
            curr_branches = next_branches
            if not curr_branches:
                break
                
        for (b0, b1, b2, b3, _, _) in curr_branches:
            plaintext = b0 + b1 + b2 + b3
            return plaintext
                
    return b""