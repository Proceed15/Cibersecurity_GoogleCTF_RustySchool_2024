# Troubleshooting & Solução de Problemas: Rusty School CTF

Este guia cobre a resolução dos erros mais comuns de dependências, ambiente, compatibilidade do SageMath e execução no desmonte do desafio **Rusty School (Google CTF 2024)**.

---

## 1. Erros e Compatibilidade do SageMath

### 1.1 `AttributeError: 'FiniteField_subfield_ext_with_category' object has no attribute 'fetch_int'`
* **Causa**: O método `.fetch_int()` foi descontinuado e removido em versões recentes do SageMath (versão 10.0+).
* **Solução**: Substitua todas as chamadas `.fetch_int(val)` por `.from_integer(int(val))` e `.integer_representation()` por `.to_integer()`.
```python
# ❌ Código antigo (SageMath < 9.8)
element = F.fetch_int(val)
val_int = element.integer_representation()

# ✅ Código atualizado (SageMath 10+)
element = F.from_integer(int(val))
val_int = element.to_integer()
```

### 1.2 `TypeError: cannot convert non-integral to integer`
* **Causa**: Passagem de tipos do Python (`numpy.uint16` ou elementos de bytes) diretamente para o construtor do SageMath sem conversão explícita.
* **Solução**: Certifique-se de envolver o valor em `int()` nativo do Python:
```python
F_solve_for = [F.from_integer(int(x)) for x in solve_for]
```

### 1.3 `ValueError: ideal is not zero-dimensional`
* **Causa**: O sistema de equações quadráticas não possui restrições suficientes, gerando um número infinito de soluções no corpo finito.
* **Solução**: Adicione o conjunto de equações correspondente a `m = 1` utilizando os valores conhecidos de `rv1`. O acoplamento dos dois sistemas reduz a dimensão do ideal para 0, permitindo o cálculo exato da variedade (`variety()`).

---

## 2. Erros de Ambiente e Execução em Python

### 2.1 `ModuleNotFoundError: No module named 'sage'`
* **Causa**: Tentativa de rodar `solve.sage` diretamente com o interpretador `python3` do sistema, em vez do runner do SageMath.
* **Solução**:
  * Para scripts `.sage`: execute com o comando `sage`:
    ```bash
    sage solve.sage
    ```
  * Para o script multiprocessado em Python (`solve_fast.py`): certifique-se de chamar o interpretador que possui as bindings do SageMath instaladas ou rodar através do Sage:
    ```bash
    sage -python solve_fast.py flag.txt.encrypted
    ```

### 2.2 `Permission denied: './patch_binary.sh'`
* **Causa**: O script de patch não possui permissões de execução no Linux.
* **Solução**:
  ```bash
  chmod +x patch_binary.sh
  ./patch_binary.sh
  ```

---

## 3. Problemas com GDB e Patching do Binário

### 3.1 `getrandom` continua retornando bytes aleatórios no GDB
* **Causa**: O binário original faz chamadas diretas à chamada de sistema `getrandom` do Linux, contornando a leitura de `/dev/urandom`.
* **Solução**:
  1. Patch no binário para alterar a string de `/dev/urandom` para `./my_urandom`.
  2. Redirecionamento do arquivo de aleatoriedade no Linux para `/dev/zero`:
     ```bash
     ln -sf /dev/zero my_urandom
     ```
  3. No GDB, force o registrador do retorno de `getrandom` (`$rax`) para o tamanho solicitado usando um breakpoint em `syscall`.

### 3.2 O binário falha com `SigABRT` ou `BufferOverflow` ao carregar a flag
* **Causa**: O arquivo `flag.txt.encrypted` está truncado ou não possui um tamanho múltiplo de 60 bytes (tamanho do bloco cifrado).
* **Solução**: Verifique o tamanho do arquivo cifrado. Ele deve possuir exatamente $133 \times 60 = 7980$ bytes.
```bash
ls -l flag.txt.encrypted
```

---

## 4. Otimização de Performance e Memória

* **Uso excessivo de CPU/RAM**: O cálculo de bases de Gröbner e variedades no SageMath pode ser exigente em CPU.
* **Solução**:
  * Ao utilizar `solve_fast.py`, limite o número de processos concorrentes ajustando a flag `--workers`:
    ```bash
    python3 solve_fast.py flag.txt.encrypted --workers 4
    ```
