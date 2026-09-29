# 🚀 Guia de Clonagem e Execução no Terminal

Este guia passo a passo explica como clonar o repositório do GitHub em uma máquina Linux/WSL2 e executar a solução completa do desafio **Google CTF 2024 - Rusty School**.

---

## 📋 1. Pré-requisitos

Certifique-se de que sua máquina possui o **Git**, **Python 3** e o **SageMath** instalados.

No Ubuntu / Debian / WSL2, instale as dependências executando:

```bash
sudo apt update && sudo apt install -y git build-essential gdb sagemath python3-pip
```

---

## 📥 2. Clonar o Repositório do GitHub

Abra o terminal e execute o comando abaixo para clonar o repositório (substitua a URL pelo link do seu repositório):

```bash
git clone https://github.com/SEU_USUARIO/rusty-school-ctf2024.git
cd rusty-school-ctf2024
```

---

## ⚙️ 3. Configurar Permissões de Execução

Conceda permissão de execução aos scripts do repositório:

```bash
chmod +x patch_binary.sh solve_fast.py
```

---

## 📦 4. Adicionar os Arquivos do Desafio

Caso os arquivos originais do CTF não estejam no repositório, coloque-os na mesma pasta:
- `rustyschool` *(binário do desafio)*
- `flag.txt.encrypted` *(arquivo cifrado contendo a flag)*

---

## 🔧 5. (Opcional) Patching para Depuração Determinística no GDB

Para depurar o binário no GDB sem aleatoriedade (`getrandom`):

```bash
./patch_binary.sh
```

Isso redirecionará a leitura de `/dev/urandom` para um arquivo local com zeros (`my_urandom`).

---

## ⚡ 6. Executar o Solver

Você tem duas opções para executar a decifração:

### Opção A: Execução Rápida via Multiprocessing (Recomendado)
Aproveita múltiplos núcleos da CPU com Python + SageMath para decifrar todos os blocos em poucos segundos:

```bash
python3 solve_fast.py flag.txt.encrypted
```

### Opção B: Solver Direto em SageMath
Executa a resolução em lote sequencial utilizando o runner do SageMath:

```bash
sage solve.sage
```

---

## 🎯 7. Verificar a Flag Decifrada

Após a execução, o resultado estará salvo no arquivo de saída decifrado:

```bash
cat flag.txt.encrypted.dec.txt
```

---

## 📤 8. Como Atualizar e Enviar Mudanças para o GitHub

Se você alterar os scripts e quiser subir las atualizações para o GitHub:

```bash
# 1. Verificar status das alterações
git status

# 2. Adicionar os arquivos alterados
git add .

# 3. Criar o commit
git commit -m "feat: atualiza scripts de resolucao e documentacao"

# 4. Enviar para o GitHub
git push origin main
```
