# Tutorial de Execução - Google CTF 2024: Rusty School

Guia direto e simplificado para configurar o ambiente, organizar os arquivos e executar o solver do desafio **Rusty School**.

---

## 1. Configuração do Ambiente (Conda + SageMath)

Como o pacote `sagemath` não está presente no APT do Ubuntu 24.04+, o método mais rápido e garantido é utilizar o **Miniforge/Conda**.

### Ativar o Conda e Criar o Ambiente
No seu terminal, rode:

```bash
# 1. Ativar o Conda na sessão atual
eval "$($HOME/miniforge3/bin/conda shell.bash hook)"

# 2. Configurar inicialização automática no .bashrc
$HOME/miniforge3/bin/conda init bash

# 3. Recarregar configurações do terminal
source ~/.bashrc

# 4. Criar o ambiente isolado com SageMath
mamba create -n sage sage -c conda-forge -y

# 5. Ativar o ambiente
conda activate sage
```

> **Nota**: Ao ativar, o prompt do terminal exibirá o prefixo `(sage)`.

---

## 2. Instalar Ferramentas Auxiliares (Opcional para Debug)

```bash
sudo apt update && sudo apt install python3 gdb -y
```

---

## 3. Preparação dos Arquivos

Coloque todos os arquivos na mesma pasta do projeto:

* **Arquivos do Desafio**: `rustyschool` (binário ELF) e `flag.txt.encrypted` (texto cifrado).
* **Scripts da Solução**: `solve_fast.py`, `solve.sage`, `cipher_model.py` e `patch_binary.sh`.

---

## 4. Execução do Solver

Com o ambiente `(sage)` ativo no terminal e dentro da pasta do projeto, execute:

### Método Rápido (Multiprocessado - Recomendado)
```bash
python3 solve_fast.py flag.txt.encrypted
```

### Método Padrão (SageMath Puro)
```bash
sage solve.sage
```

---

## 5. Visualizar a Flag Decifrada

Após a conclusão do script, exiba o conteúdo do arquivo de saída:

```bash
cat flag.txt.encrypted.dec.txt
```
