# WriteUp: Google CTF 2024 — Rusty School

**Categoria:** Reverse Engineering / Cryptography  
**Pontuação:** 406 pontos (6 solves) [134, 135]  
**Autores da Solução:** `perfect blue` (superfashi, Riatre, cts) [134, 135]  
**Binário:** ELF 64-bit x86-64 (compilado com `rustc 1.70.0`) [134]  

---

## 1. Resumo Executivo & Visão Geral

O desafio **Rusty School** do Google CTF 2024 apresenta um executável binário escrito em Rust que realiza a cifragem de arquivos [8, 134, 135]. O programa divide a entrada em blocos independentes de 48 bytes e gera saídas de 60 bytes (adicionando 12 bytes de estado aleatório para garantir a reversibilidade do processo) [8, 139].

A estrutura criptográfica consiste em uma **Rede Feistel de 4 ramos** executada ao longo de 12 rodadas por bloco [8, 143, 144]. A derivação de chaves (*key schedule*) opera em um corpo finito $GF(2^{16})$ estendido pelo polinômio redutor $x^{16} + x^5 + x^3 + x + 1$ (`0x2B`) [8, 134, 145]. A inversão do mecanismo requer a resolução de um sistema de equações quadráticas em SageMath via variedades algébricas [8, 146, 147], além do tratamento do *backtracking* para gerenciar múltiplas raízes candidatas [148, 183, 184].

---

## 2. Engenharia Reversa em Rust: Desafios e Análise Dinâmica

Analisar binários Rust em descompiladores convencionais (como IDA Pro ou Hex-Rays) é notoriamente complexo [8, 135]. O açúcar sintático do Rust (como o operador `?`), o tratamento de exceções, os gerenciadores de alocação de memória e as otimizações agressivas do LLVM geram dezenas de linhas de código de suporte (*boilerplate*) para operações simples [135, 136].

Frente a essa verbosidade, a abordagem mais eficaz foi a **análise dinâmica combinada com patching** [8, 139-141]:

1. **Identificação da chamada de sistema `getrandom`**: Verificou-se que o executável gera 12 bytes aleatórios por bloco via `getrandom` [139, 140].
2. **Patching para Determinismo**: No editor hexadecimal, alterou-se a variável indicadora de disponibilidade do `getrandom` para `0` e redirecionou-se o caminho `/dev/urandom` para `./my_urandom` [8, 141]. Criando um link simbólico `ln -s /dev/zero ./my_urandom`, o comportamento do gerador tornou-se 100% reproduzível no GDB [141].
3. **Redução das Rodadas**: Para facilitar a depuração no GDB, alterou-se temporariamente o contador de rodadas de 12 para 1 rodada [143].

---

## 3. Arquitetura da Cifra Feistel de 4 Ramos

A cifra opera sobre 4 ramos de 12 bytes cada ($b_0, b_1, b_2, b_3$), totalizando 48 bytes de texto plano [8, 144]. Em cada uma das 12 rodadas:

1. **Derivação das Chaves de Rodada**: A partir de um *seed* de 12 bytes $rv_0$, derivam-se $rv_0' = 	ext{derive}(rv_0, m=0)$ e $rv_1 = 	ext{derive}(rv_0, m=1)$ [144].
2. **Mistura das Funções Hash**:
   $$	ext{cb}_1 = b_0 \oplus 	ext{MD5}(rv_0 \mathbin{\Vert} b_2)[:12]$$ [144]
   $$	ext{cb}_2 = b_1 \oplus 	ext{SHA1}(rv_1 \mathbin{\Vert} 	ext{bs})[:12]$$ [144]
3. **Transformação Modular no Primo $P$**:
   Convertendo os ramos para inteiros *little-endian*, calcula-se:
   $$	ext{bs} = \left((i_1 + i_3) \cdot i_0 + i_2^{i_1} \pmod Pight) \pmod P$$ [144]
   Onde $P = 79160129948973046149879599747$ ($2^{96} - 17$) é um número primo de 96 bits (12 bytes) [142, 179].
4. **Permutação dos Ramos**: Os ramos são rotacionados para a próxima rodada como $(b_2, 	ext{cb}_1, 	ext{bs}, 	ext{cb}_2)$ [144].

---

## 4. Função de Derivação de Chaves e Modelagem em $GF(2^{16})$

A função `derive` recebe 12 bytes (interpretados como um vetor $a = (a_0, a_1, a_2, a_3, a_4, a_5)$ de 6 elementos em $GF(2^{16})$) e retorna 12 bytes [145, 180]:

$$	ext{derive}(a) = egin{cases}
egin{pmatrix}
a_0 a_1 + a_4 \
a_1 a_2 + a_5 \
a_2 a_3 + a_0 \
a_3 a_4 + a_1 \
a_4 a_5 + a_2 \
a_5 a_0 + a_3
\end{pmatrix} & 	ext{para } m = 0 \[2ex]
egin{pmatrix}
a_2 a_3 + a_5 \
a_3 a_4 + a_0 \
a_4 a_5 + a_1 \
a_5 a_0 + a_2 \
a_0 a_1 + a_3 \
a_1 a_2 + a_4
\end{pmatrix} & 	ext{para } m = 1
\end{cases}$$ [146, 180]

Para inverter a função `derive`, constrói-se um **sistema de 6 equações polinomialmente quadráticas em 6 variáveis** sobre o corpo finito $GF(2^{16})$ com o polinômio redutor $x^{16} + x^5 + x^3 + x + 1$ (`0x2B`) [8, 145-147, 180].

---

## 5. Implementação do Solver no SageMath e Correções de API

A inversão algébrica utiliza **Ideais de Anéis de Polinômios e Variedades Algébricas** em SageMath (`Ideal.variety()`) [146, 147, 180].

### Migração de API (SageMath 10+)
O script original utilizava o método legado `.fetch_int()`, descontinuado nas versões modernas do SageMath (como a versão 10.9 no Conda) [134]. A solução foi atualizar as chamadas para os métodos oficiais `.from_integer()` e `.to_integer()` [134, 180].

### Inversão Estrita do 4º Ramo Feistel
Para evitar erros de conversão (`OverflowError`), a inversão do ramo de mistura modular deve manter o resultado estritamente no intervalo $[0, P-1]$:
$$b_3 = \left(\left(\left((	ext{bs} - b_2^{b_1} \pmod P) \cdot b_0^{-1} \pmod Pight) - b_1 \pmod Pight) \pmod Pight).	ext{to\_bytes}(12, 	ext{'little'})$$ [183]

---

## 6. Algoritmo de Busca em Profundidade (DFS) e Multiprocessamento

Como o sistema quadrático em $GF(2^{16})$ pode admitir mais de uma raiz válida por rodada, o algoritmo realiza uma **Busca em Profundidade (DFS)** revertendo as 12 rodadas de trás para frente [148, 183, 184]. Para rodadas intermediárias, utilizam-se as equações combinadas de $m=0$ e $m=1$ (`solve2`), restringindo a variedade a soluções únicas [148, 181, 183].

Devido à independência dos 133 blocos de 60 bytes do arquivo cifrado (`flag.txt.encrypted`), a decifração foi otimizada utilizando `multiprocessing` com o método `spawn` [148, 185], completando a execução em aproximadamente 85 segundos [128].

---

## 7. Código do Solver (`solve.py`)

```python
import os
import hashlib
import struct
from sage.all import *

P = 79160129948973046149879599747

def p16(x):
    return struct.pack("<H", x)

def u16(x):
    return struct.unpack("<H", x)[0]

def xor(a: bytes, b: bytes) -> bytes:
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

def solve_(solve_for, m):
    R = PolynomialRing(GF(2), names=('x',))
    (x,) = R._first_ngens(1)
    irreducible_poly = x**16 + x**5 + x**3 + x + 1
    F = GF(2**16, modulus=irreducible_poly, name='a')

    F_solve_for = [F.from_integer(int(val)) for val in solve_for]
    G = PolynomialRing(F, names=('a0', 'a1', 'a2', 'a3', 'a4', 'a5'))
    a0, a1, a2, a3, a4, a5 = G.gens()

    if m == 0:
        my_id = Ideal([
            a0 * a1 + a4 - F_solve_for[0],
            a1 * a2 + a5 - F_solve_for[1],
            a2 * a3 + a0 - F_solve_for[2],
            a3 * a4 + a1 - F_solve_for[3],
            a4 * a5 + a2 - F_solve_for[4],
            a5 * a0 + a3 - F_solve_for[5],
        ])
    elif m == 1:
        my_id = Ideal([
            a2 * a3 + a5 - F_solve_for[0],
            a3 * a4 + a0 - F_solve_for[1],
            a4 * a5 + a1 - F_solve_for[2],
            a5 * a0 + a2 - F_solve_for[3],
            a0 * a1 + a3 - F_solve_for[4],
            a1 * a2 + a4 - F_solve_for[5],
        ])
    assert my_id.dimension() == 0
    my_variety = my_id.variety()
    return [[
        variety[a0].to_integer(),
        variety[a1].to_integer(),
        variety[a2].to_integer(),
        variety[a3].to_integer(),
        variety[a4].to_integer(),
        variety[a5].to_integer()
    ] for variety in my_variety]

def solve2_(rv0, rv1):
    R = PolynomialRing(GF(2), names=('x',))
    (x,) = R._first_ngens(1)
    irreducible_poly = x**16 + x**5 + x**3 + x + 1
    F = GF(2**16, modulus=irreducible_poly, name='a')

    rv0 = [F.from_integer(int(val)) for val in rv0]
    rv1 = [F.from_integer(int(val)) for val in rv1]

    G = PolynomialRing(F, names=('a0', 'a1', 'a2', 'a3', 'a4', 'a5'))
    a0, a1, a2, a3, a4, a5 = G.gens()
    my_id = Ideal([
        a0 * a1 + a4 - rv0[0],
        a1 * a2 + a5 - rv0[1],
        a2 * a3 + a0 - rv0[2],
        a3 * a4 + a1 - rv0[3],
        a4 * a5 + a2 - rv0[4],
        a5 * a0 + a3 - rv0[5],
        a2 * a3 + a5 - rv1[0],
        a3 * a4 + a0 - rv1[1],
        a4 * a5 + a1 - rv1[2],
        a5 * a0 + a2 - rv1[3],
        a0 * a1 + a3 - rv1[4],
        a1 * a2 + a4 - rv1[5],
    ])
    assert my_id.dimension() == 0
    my_variety = my_id.variety()
    return [[
        variety[a0].to_integer(),
        variety[a1].to_integer(),
        variety[a2].to_integer(),
        variety[a3].to_integer(),
        variety[a4].to_integer(),
        variety[a5].to_integer()
    ] for variety in my_variety]

def solve(rv, m):
    sol = solve_([u16(rv[i * 2 : i * 2 + 2]) for i in range(6)], m)
    return [b"".join(p16(x) for x in y) for y in sol]

def solve2(rv0, rv1):
    sol = solve2_([u16(rv0[i * 2 : i * 2 + 2]) for i in range(6)], [u16(rv1[i * 2 : i * 2 + 2]) for i in range(6)])
    return [b"".join(p16(x) for x in y) for y in sol]

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

def do_chunk(output):
    assert len(output) == 60
    POSSIBLE_OUTPUTS = []
    rv1 = output[48:60]
    for pot_old_rv0 in solve(rv1, m=1):
        POSSIBLE_OUTPUTS.append((output[:48], derive(pot_old_rv0, m=0), rv1))

    for n in range(N_ROUNDS):
        POSSIBLE_OLD_INPUTS = []
        for output_bytes, rv0_b, rv1_b in POSSIBLE_OUTPUTS:
            POSSIBLE_OLD_INPUTS.extend(do_one_round(output_bytes, rv0_b, rv1_b, n))
        POSSIBLE_OLD_INPUTS = list(set(POSSIBLE_OLD_INPUTS))
        POSSIBLE_OUTPUTS = POSSIBLE_OLD_INPUTS

    for orig_input, _, _, _ in POSSIBLE_OLD_INPUTS:
        if all((c >= 0x20 and c < 0x7f) or c in [0xa, 0xd] for c in orig_input):
            return orig_input
    return b'[CHUNK FAILED TO DECRYPT]'
```

---

## 8. Conclusão e Resultados

A combinação da análise de engenharia reversa dinâmica com a modelagem em corpo finito $GF(2^{16})$ permitiu reverter completamente a cifra do desafio **Rusty School**. A correção da compatibilidade com o SageMath 10+ e o ajuste dos limites aritméticos garantiram a decifração dos 133 blocos do arquivo sem falhas de execução [8, 128, 134].
