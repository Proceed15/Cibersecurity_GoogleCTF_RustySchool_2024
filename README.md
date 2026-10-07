# Google CTF 2024 + Rusty School (Reversing / Crypto)

> **WriteUp & Solução Oficial** do desafio **Rusty School** do Google CTF 2024.
> **Pontuação:** 406 pts | **Solves:** 6 | **Autores:** Google CTF / perfect blue

---

## Visão Geral do Desafio

O desafio consiste na análise de um executável ELF x86-64 compilado em **Rust** (`rustyschool`) que implementa uma cifra de bloco proprietária baseada em uma **Rede Feistel de 4 ramos** com 12 rodadas e evolução de chaves sobre o corpo finito $\text{GF}(2^{16})$.

Para recuperar a mensagem original em texto plano a partir do arquivo cifrado (`flag.txt.encrypted`), a solução exige:
1. **Engenharia Reversa no Binário Rust**: Mapeamento das estruturas internas, chamadas de dispersão (`MD5`, `SHA-1`) e redução modular com o primo de 96 bits $P = 79160129948973046149879599747$.
2. **Criptoanálise Algébrica em $\text{GF}(2^{16})$**: Formulação e resolução do sistema não linear de 6 equações quadráticas sobre o polinômio redutor irredutível $x^{16} + x^5 + x^3 + x + 1$ (`0x2B`).
3. **Solver em SageMath 10+**: Atualização da API do SageMath (`from_integer` / `to_integer`) e busca recursiva em profundidade (*backtracking*) multiprocessada para decifrar os 133 blocos de 60 bytes.

---

## Estrutura do Repositório (Arquivos Principais)

```text
.
├── attachments/                 # Arquivos fornecidos no desafio
│   ├── flag.txt.encrypted       # Arquivo cifrado de 7.980 bytes (133 blocos)
│   └── rustyschool              # Binário ELF x86-64 compilado em Rust
├── challenge/
│   └── src/                     # Código-fonte original do desafio em Rust
├── solution/
│   ├── flag.txt                 # Flag oficial recuperada (Arte ASCII)
│   └── solve.sage               # Script de solução original em SageMath
├── metadata.yaml                # Manifesto do desafio (padrão ctf-cli)
├── solve.py                     # Módulo de inversão algébrica (SageMath 10+)
├── solve_fast.py                # Orquestrador multiprocessado paralelizável
└── README.md                    # Documentação do repositório
```

---

## Requisitos e Pré-requisitos

* **Sistema Operacional**: Linux (Ubuntu 22.04 LTS / WSL2)
* **Python**: 3.10 ou superior
* **SageMath**: Versão 10.0+ (instalação via Conda recomendada)

### Configuração do Ambiente Conda

```bash
# Ativar o ambiente Conda contendo o SageMath
conda activate sage
```

---

## Como Executar o Solver (*Quick Start*)

1. **Clone o repositório e navegue até a pasta**:
   ```bash
   git clone https://github.com/seu-usuario/google-ctf-2024-rustyschool.git
   cd google-ctf-2024-rustyschool
   ```

2. **Execute o solver multiprocessado**:
   ```bash
   PYTHONPATH=. python3 solve_fast.py attachments/flag.txt.encrypted
   ```

3. **Verifique o resultado**:
   O script executará primeiro a **Fase 0 (Prova de Conceito do Bloco #0)** e em seguida processará os 133 blocos em paralelo. O resultado final será salvo em `solution/flag.txt`.

   ```bash
   cat solution/flag.txt
   ```

---

## Detalhes da Solução Algébrica

### 1. Inversão da Derivação de Chaves (`derive`)
A função de chave deriva o estado inicial em $\text{GF}(2^{16})$ resolvendo o Ideal polinomial de 6 equações quadráticas:
$$a_i \cdot a_{i+1} + a_{i+4} = c_i \pmod{x^{16} + x^5 + x^3 + x + 1}$$

### 2. Inversão dos Ramos Feistel por Rodada
Para cada uma das 12 rodadas Feistel (de trás para frente):
1. $b_1 = \text{cb}_2 \oplus \text{SHA1}(rv_1 \parallel b_2)[:12]$
2. $b_0 = \text{cb}_1 \oplus \text{MD5}(rv_0 \parallel b_2)[:12]$
3. $b_3 = \left[ \left( (\text{bs} - b_2^{b_1} \pmod P) \cdot b_0^{-1} \pmod P - b_1 \right) \pmod P \right] \text{.to\_bytes}(12, \text{'little'})$

---

## Flag Decifrada

A flag é um banner visual completo em **Arte ASCII** com a marca oficial do **Google CTF 2024**:
```text
 .d8888b. 88888888888 8888888888 .d888 8888888 
d88P  Y88b    888     888       d88P"    888   
888    888    888     888      d88P      888   
888           888     8888888 d88P       888   
888  88888    888     888    d88P        888   
888    888    888     888   d88P         888   
Y88b  d88P    888     888  d88P          888   
 "Y8888P8"    888     888 d88P       888888888 
```

