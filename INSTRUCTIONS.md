# Guia de Instruções de Execução: Rusty School CTF

Este documento fornece um passo a passo detalhado para configurar o ambiente, realizar a análise dinâmica no GDB, compilar os scripts e executar o solver de decifração do desafio **Rusty School**.

---

## 1. Preparação do Ambiente

### Requisitos do Sistema
* **SO**: Ubuntu 22.04 LTS / 24.04 LTS (ou Debian/WSL2 no Windows)
* **Ferramentas**: `gdb`, `sage`, `python3`, `gcc`, `make`

### Instalação de Pacientes e Dependências
Execute no terminal:
```bash
sudo apt update && sudo apt install -y \
    build-essential \
    gdb \
    strace \
    sagemath \
    python3 \
    python3-pip \
    git
```

---

## 2. Estrutura dos Arquivos do Projeto

Certifique-se de manter todos os arquivos na mesma pasta de trabalho:

```text
rusty_school/
├── rustyschool          # Binário ELF x86-64 do desafio
├── flag.txt.encrypted  # Arquivo contendo a flag cifrada
├── patch_binary.sh      # Script para patching de determinismo
├── cipher_model.py      # Modelo em Python da cifra Feistel
├── solve.sage           # Solver em SageMath (Sistemas sobre GF(2^16))
├── solve_fast.py        # Solver otimizado com multiprocessing
├── INSTRUCTIONS.md      # Este guia de instruções
└── TROUBLESHOOTING.md  # Guia de solução de problemas
```

---

## 3. Passo a Passo de Execução

### Passo 1: Aplicar o Patch de Determinismo (Análise Dinâmica)
Para analisar o comportamento da cifra no GDB sem a interferência de bytes aleatórios:

```bash
chmod +x patch_binary.sh
./patch_binary.sh
```
> O script substituirá a string `/dev/urandom` no binário por `./my_urandom` apontando para `/dev/zero`.

---

### Passo 2: Testar o Modelo da Cifra em Python
Valide se as funções de rodada (MD5, SHA-1, operação modular com primo $P$) estão operando corretamente:

```bash
python3 cipher_model.py
```

---

### Passo 3: Decifração Sequencial via SageMath
Para testar a inversão do sistema quadrático sobre $GF(2^{16})$ em um único bloco cifrado:

```bash
sage solve.sage
```

---

### Passo 4: Decifração Completa e Rápida (Multiprocessing)
Para decifrar todos os 133 blocos do arquivo `flag.txt.encrypted` em paralelo utilizando todos os núcleos do processador:

```bash
python3 solve_fast.py flag.txt.encrypted
```

O script criará o arquivo `flag.txt.encrypted.dec.txt` contendo a flag recuperada e imprimirá o resultado no terminal:
```text
[+] Decifração concluída com sucesso!
[+] Flag: CTF{...}
```

---

## 4. Análise Adicional no GDB (Opcional)

Se desejar depurar os registradores da função `derive` manualmente:

1. Inicie o GDB com o binário alterado:
   ```bash
   gdb ./rustyschool
   ```
2. Defina um breakpoint na função de derivação de chave:
   ```gdb
   (gdb) break *derive
   (gdb) run flag.txt.encrypted
   ```
3. Inspecione os parâmetros passados no registrador `$rdi` (ponteiro para a semente de 12 bytes).
