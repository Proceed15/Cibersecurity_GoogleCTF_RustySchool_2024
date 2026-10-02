import hashlib

# Primo P de 96 bits (12 bytes) utilizado no binário do Rusty School
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

def u16(b): 
    return int.from_bytes(b, 'little')

def p16(x): 
    return (x & 0xFFFF).to_bytes(2, 'little')

def xor(b1, b2): 
    return bytes(x ^ y for x, y in zip(b1, b2))

def derive(seed: bytes, *, m: int) -> bytes:
    """
    Função de derivação de chave em GF(2^16) com o polinômio x^16 + x^5 + x^3 + x + 1 (0x2B).
    """
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

def process_block(block: bytes, random_bytes_fn, rounds=12) -> bytes:
    """
    Rede Feistel de 4 ramos processando blocos de 48 bytes em 60 bytes cifrados.
    """
    assert len(block) == 48
    rv0 = random_bytes_fn(12)
    b = [block[i * 12 : (i + 1) * 12] for i in range(4)]
    
    for _ in range(rounds):
        i_vals = [int.from_bytes(x, "little") for x in b]
        rv0, rv1 = derive(rv0, m=0), derive(rv0, m=1)
        
        cb1 = xor(hashlib.md5(rv0 + b[0]).digest()[:12], b[1])
        bs = ((i_vals[0] + i_vals[1]) * i_vals[2] + pow(i_vals[3], i_vals[0], P)) % P
        bs_bytes = bs.to_bytes(12, "little")
        cb2 = xor(hashlib.sha1(rv1 + bs_bytes).digest()[:12], b[3])
        
        b = [b[1], cb1, bs_bytes, cb2]

    return rv0 + b"".join(b)
