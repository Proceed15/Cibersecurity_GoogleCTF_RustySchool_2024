# Guia de Configuração do Ambiente SageMath via Conda no WSL (Ubuntu 24.04+)

Este guia detalha o processo exato para instalar o **SageMath** e executar o solver do desafio **Rusty School** dentro do **WSL (Windows Subsystem for Linux)** usando o **Miniforge (Conda/Mamba)**.

---

## 1. Por que usar Conda no WSL?

No Ubuntu 24.04 LTS (Noble Numbat) e distribuições mais recentes, o pacote `sagemath` foi removido dos repositórios oficiais do `apt` por incompatibilidades na transição para o Python 3.12. 

O **Miniforge (Conda-Forge)** resolve esse problema fornecendo uma build pré-compilada, isolada e atualizada do SageMath, que roda perfeitamente no WSL sem afetar os pacotes do sistema.

---

## 2. Passo a Passo de Instalação no WSL

### Passo 1: Baixar e Executar o Instalador do Miniforge
Abra o seu terminal WSL (Ubuntu) e execute:

```bash
# 1. Baixar o instalador do Miniforge3
curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"

# 2. Executar o script de instalação
bash Miniforge3-Linux-x86_64.sh
```

> **Dica**: Durante a instalação, pressione `ENTER` para ler a licença, digite `yes` para aceitar e confirme o local de instalação padrão (`$HOME/miniforge3`).

---

### Passo 2: Ativar e Inicializar o Shell (Tratando o aviso do Conda)

Caso você opte por não permitir que o instalador altere automaticamente os seus scripts de inicialização, inicialize o Conda manualmente com os comandos abaixo:

```bash
# 1. Ativar o Conda na sessão atual do terminal
eval "$($HOME/miniforge3/bin/conda shell.bash hook)"

# 2. Configurar o Conda para inicializar automaticamente no seu .bashrc
$HOME/miniforge3/bin/conda init bash

# 3. Recarregar o arquivo de configuração do terminal
source ~/.bashrc
```

*Se o seu terminal utilizar `zsh` em vez de `bash`, substitua `bash` por `zsh` nos comandos acima.*

---

### Passo 3: Criar o Ambiente Virtual com SageMath

Com o Conda ativo (você verá a indicação `(base)` no seu prompt), crie o ambiente isolado `sage`:

```bash
# 1. Criar o ambiente virtual contendo o SageMath via conda-forge
mamba create -n sage sage -c conda-forge -y

# 2. Ativar o ambiente criado
conda activate sage
```

> **Confirmação**: O prompt passará a exibir `(sage)`. Para testar a instalação, digite:
> ```bash
> sage --version
> ```

---

## 3. Execução do Solver no WSL

### Passo 1: Navegar até a pasta do projeto

No WSL, você pode acessar seus arquivos locais ou clonar o repositório do projeto:

```bash
cd /caminho/para/o/repositorio/rusty_school
```

### Passo 2: Executar o Solver

Com o ambiente `(sage)` ativo, execute o script otimizado em Python ou o script em SageMath:

```bash
# Opção Rápida (Multiprocessado em Python/SageMath)
python3 solve_fast.py flag.txt.encrypted

# Opção Padrão em SageMath
sage solve.sage
```

### Passo 3: Ler a Flag Decifrada

```bash
cat flag.txt.encrypted.dec.txt
```

---

## 4. Dicas Úteis para WSL

1. **Acessando arquivos do Windows pelo WSL**:
   Seus discos do Windows estão montados em `/mnt/c/`. Exemplo:
   ```bash
   cd /mnt/c/Users/SeuUsuario/Desktop/rusty_school
   ```

2. **Ajustar permissões de scripts**:
   Caso copie os arquivos do Windows para o Linux, garanta permissão de execução nos scripts shell:
   ```bash
   chmod +x patch_binary.sh
   ```

3. **Desativar o ambiente Conda ao finalizar**:
   ```bash
   conda deactivate
   ```
