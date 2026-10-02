# Google CTF 2024 - Rusty School (Reversing / Cryptography)

[![Category](https://img.shields.io/badge/Category-Reversing%20%2F%20Crypto-blue.svg)](#)
[![Points](https://img.shields.io/badge/Points-406-orange.svg)](#)
[![Solves](https://img.shields.io/badge/Solves-6-red.svg)](#)
[![Rust](https://img.shields.io/badge/Rust-1.70.0-black.svg)](#)
[![SageMath](https://img.shields.io/badge/SageMath-10.x%2B-green.svg)](#)

Este repositório contém a solução completa, modelo da cifra, scripts de patching e o solver algébrico paralelizado para o desafio **Rusty School** do **Google CTF 2024 (Quals)**.

---

## 📌 Visão Geral do Desafio

* **Nome**: Rusty School
* **Categoria**: Reversing / Cryptography
* **Pontuação**: 406 pontos (6 soluções durante a competição)
* **Arquivos do Desafio**:
  * `rustyschool`: Executável ELF x86-64 não-stripado compilado em Rust 1.70.0
  * `flag.txt.encrypted`: Arquivo contendo a flag cifrada em blocos

---

## 🔬 Análise do Binário e Cifra

### 1. Estrutura de Blocos e Não-determinismo
* O binário processa a entrada em **blocos de 48 bytes** e gera **blocos cifrados de 60 bytes**.
* Para cada bloco, o programa obtém 12 bytes aleatórios via `getrandom` syscall e os inclui no bloco cifrado, tornando o processo invertível.
* **Tamanho total**: O arquivo `flag.txt.encrypted` possui 133 blocos cifrados independentes.

### 2. Arquitetura da Cifra Feistel
* **Estrutura**: Rede Feistel de 4 ramos com **12 rodadas (rounds)** por bloco.
* **Operações de Rodada**:
  * XOR com digests parciais de **MD5** e **SHA-1**.
  * Aritmética modular utilizando um número primo grande $P$ como módulo.
* **Escalonamento de Chaves (`derive`)**:
  * A função `derive(seed, m)` opera sobre um vetor de 6 elementos no corpo finito $\text{GF}(2^{16})$.
  * Usa o polinômio redutor irredutível $x^{16} + x^5 + x^3 + x + 1$ (`0x2B`).
  * O parâmetro booleano $m \in \{0, 1\}$ define qual ramo do sistema de equações quadráticas é utilizado para gerar as chaves de rodada ($rv_0$ e $rv_1$).

---

## 🎯 Estratégia de Resolução

### Passo 1: Patching para Determinismo no GDB
Para contornar o não-determinismo introduzido pela chamada `getrandom`, altera-se a string interna `/dev/urandom` no binário para `./my_urandom` apontando para `/dev/zero`. Isso permite depurar a execução de forma reproduzível.

```bash
bash patch_binary.sh
```

### Passo 2: Inversão Algébrica no SageMath
A inversão da função `derive` se reduz a resolver um **sistema quadrático de 6 equações com 6 variáveis** sobre $\text{GF}(2^{16})$:

$$\text{derive}(a) = \begin{cases}
\begin{pmatrix} a_0 a_1 + a_4 \\ a_1 a_2 + a_5 \\ a_2 a_3 + a_0 \\ a_3 a_4 + a_1 \\ a_4 a_5 + a_2 \\ a_5 a_0 + a_3 \end{pmatrix} & m = 0 \\[2ex]
\begin{pmatrix} a_2 a_3 + a_5 \\ a_3 a_4 + a_0 \\ a_4 a_5 + a_1 \\ a_5 a_0 + a_2 \\ a_0 a_1 + a_3 \\ a_1 a_2 + a_4 \end{pmatrix} & m = 1
\end{cases}$$

O **SageMath** calcula a variedade algébrica do ideal polinomial correspondente (`my_id.variety()`). Para lidar com soluções múltiplas em rodadas intermediárias, combinam-se as equações de $m=0$ e $m=1$ para restringir o espaço de busca recursivamente.

---

## 📁 Estrutura dos Arquivos do Projetos

| Arquivo | Descrição |
| :--- | :--- |
| **`solve.sage`** | Solver algébrico principal em SageMath. Resolve os ideais polinomiais em $\text{GF}(2^{16})$ com suporte a SageMath 10.x+ (`from_integer` / `to_integer`). |
| **`solve_fast.py`** | Wrapper em Python com `ProcessPoolExecutor` para decifração paralela dos 133 blocos em multi-core. |
| **`cipher_model.py`** | Modelo em Python puro da cifra Feistel de 4 ramos e da função `derive`. |
| **`patch_binary.sh`** | Script de patch em Bash para garantir execuções determinísticas no GDB. |

---

## 🛠️ Como Executar

### Pré-requisitos
Instale as dependências no Ubuntu/Debian ou WSL2:
```bash
sudo apt update
sudo apt install sagemath python3 gdb
```

### Executando o Solver
Para decifrar a flag de forma paralela e rápida:

```bash
python3 solve_fast.py flag.txt.encrypted
```

> **Tempo estimado**: ~30-60 segundos em CPUs multi-core modernas (~4 minutos em single-thread).

---

## 📝 Licença e Créditos
* **Desafio**: Criado pela equipe do Google CTF 2024.
* **Write-up de Referência**: *cts / perfectblue* (Google CTF 2024 Quals).


