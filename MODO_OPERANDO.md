# Modo Operando (SOP) & Checklist para Apresentação - Google CTF 2024: Rusty School

Este documento descreve o **Modo Operando** (passo a passo para execução técnica no terminal WSL/Linux) e os **Requisitos de Conteúdo para Apresentação** do desafio **Rusty School**.

---

## 🚀 Parte 1: Modo Operando (Passo a Passo de Execução)

### 1. Preparação do Ambiente WSL (Conda + SageMath)
Se ainda não configurou o ambiente Conda com o SageMath no WSL (Ubuntu 24.04):

```bash
# 1. Ativar o Conda na sessão do terminal
eval "$($HOME/miniforge3/bin/conda shell.bash hook)"

# 2. Ativar o ambiente com SageMath
conda activate sage
```

### 2. Organização e Obtenção dos Arquivos
Navegue até a pasta do desafio e garanta a presença do arquivo cifrado oficial:

```bash
# 1. Criar e acessar o diretório do projeto
mkdir -p ~/rusty_school && cd ~/rusty_school

# 2. Baixar o arquivo cifrado oficial do desafio
wget https://raw.githubusercontent.com/perfectblue/ctf-writeups/master/2024/googlectf-2024/rev-rustyschool/flag.txt.encrypted

# 3. Confirmar a presença dos scripts do repositório
ls -la
# Devem estar presentes: solve_fast.py, solve.sage, cipher_model.py, patch_binary.sh
```

### 3. Patching e Depuração Dinâmica (Opcional - Fase de Reversing)
Para analisar o binário `rustyschool` no GDB de forma determinística:

```bash
# Dar permissão e aplicar o patch no binário
chmod +x patch_binary.sh
./patch_binary.sh
```

### 4. Execução do Solver Multiprocessado
Rode o solver otimizado para decifrar os 133 blocos em paralelo:

```bash
# Com o ambiente (sage) ativo:
python3 solve_fast.py flag.txt.encrypted
```

### 5. Leitura do Resultado
Exiba a flag decifrada no terminal:

```bash
cat flag.txt.encrypted.dec.txt
```

---

## 📋 Parte 2: Checklist e Conteúdo Requerido para a Apresentação

Com base no levantamento das fontes e write-ups oficiais, a apresentação técnica deve abordar obrigatoriamente as seguintes seções para demonstrar domínio completo do desafio:

### 1. A Problemática do Reversing em Binários Rust
* **Desafio da Descompilação**: Explicar por que binários Rust geram códigos pseudo-C extremamente verbosos e ruidosos no Hex-Rays/IDA Pro (tratamento de erros, macros `?`, inlining e chamadas funcionais) [6, 7].
* **Análise Dinâmica no GDB**: Mostrar como a análise por depurador foi essencial para observar as leituras da chamada `getrandom` de 48 bytes e o retorno de 60 bytes cifrados (48 bytes + 12 bytes de semente aleatória) [10].

### 2. Arquitetura da Cifra de Bloco
* **Estrutura Feistel de 4 Ramos**: Demonstrar a rede Feistel customizada operando em 12 rodadas com funções de confusão baseadas em hashes MD5, SHA1 e aritmética modular utilizando um primo $P$ fixo [13, 16].
* **Determinismo via Patching**: Explicar a técnica de alterar `/dev/urandom` para `./my_urandom` no binário para fixar sementes nulas no GDB [12].

### 3. A Ponte entre Reversing e Criptografia ($\text{GF}(2^{16})$)
* **Função `derive`**: Mostrar a transição da função bitwise do binário em Rust para a formulação algébrica no corpo finito $\text{GF}(2^{16})$ com o polinômio redutor $x^{16} + x^5 + x^3 + x + 1$ (`0x2B`) [15, 16].
* **Inversão da Chave**: Detalhar a montagem do sistema quadrático de 6 equações a 6 variáveis para recuperar as chaves a cada rodada [17].

### 4. Resolução Algébrica no SageMath
* **Correção de Compatibilidade da API**: Registrar a atualização necessária do código para o SageMath 10+ (substituição do método legado `.fetch_int()` por `.from_integer()` e `.to_integer()`) [5].
* **Demostração de Inversão em 1 Bloco**: Mostrar a prova de conceito invertendo um único bloco de 48 bytes antes de estender o script para a execução paralela dos 133 blocos [5, 19].

### 5. Dados Competitivos
* **Google CTF 2024**: Resolução do desafio na categoria *Reversing* com pontuação de **406 pontos** e apenas **6 solves** globais em 48 horas [5, 6].
