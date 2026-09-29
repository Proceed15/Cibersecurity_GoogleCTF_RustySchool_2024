# Solução para o Erro de Instalação do SageMath (`E: Package 'sagemath' has no installation candidate`)

Este guia resolve o erro comum de instalação do **SageMath** em distribuições Linux (Ubuntu, Debian, WSL) onde o repositório necessário não está ativado por padrão.

---

## 📌 Descrição do Problema

Ao tentar executar:
```bash
sudo apt install sagemath python3 gdb
```

O gerenciador de pacotes `apt` retorna o seguinte erro:
```text
Reading package lists... Done
Building dependency tree... Done
Reading state information... Done
Package sagemath is not available, but is referred to by another package.
This may mean that the package is missing, has been obsoleted, or
is only available from another source

E: Package 'sagemath' has no installation candidate
```

---

## 🔍 Causa Raiz

Em instalações minimalistas de sistemas baseados em Debian/Ubuntu (incluindo **WSL2 no Windows**, instâncias na nuvem como AWS/GCP e contêineres Docker), o repositório **`universe`** (que abriga o pacote `sagemath`) vem desativado por padrão.

---

## 🛠️ Solução 1: Ativar o Repositório `universe` (Recomendado)

Rode os seguintes comandos no terminal:

```bash
# 1. Adiciona o repositório universe
sudo add-apt-repository universe -y

# 2. Atualiza a lista de pacotes do apt
sudo apt update

# 3. Tenta instalar o SageMath e dependências novamente
sudo apt install -y sagemath python3 gdb
```

Após isso, verifique a instalação executando:
```bash
sage --version
```

---

## 🚀 Solução 2: Instalação via Conda / Mamba (Sem root ou para distribuições alternativas)

Se você não tiver permissão de `sudo` ou preferir gerenciar o ambiente via Python/Conda:

```bash
# 1. Instale o Miniconda ou Mamba (se ainda não tiver)
# 2. Crie um ambiente com SageMath
conda create -n sage-env -c conda-forge sage python=3.10
conda activate sage-env

# 3. Verifique a instalação
sage --version
```

---

## 🐳 Solução 3: Executar via Docker (Sem instalar no sistema operacional)

Se preferir não baixar gigabytes de pacotes no seu sistema local, use a imagem oficial do SageMath via Docker:

```bash
# Executa o solver dentro do contêiner Docker oficial montando a pasta atual
docker run --rm -v "$(pwd):/workspace" -w /workspace sagemath/sagemath sage solve.sage
```

---

## 📝 Atualização nos Arquivos de Instruções

Se estiver compartilhando o repositório, certifique-se de instruir os usuários a rodar `sudo add-apt-repository universe` antes de executar os scripts de setup.
