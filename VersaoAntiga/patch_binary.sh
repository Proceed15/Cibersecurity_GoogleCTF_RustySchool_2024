#!/bin/bash
# ==============================================================================
# patch_binary.sh - Torna o binário Rusty School determinístico para o GDB
# ==============================================================================

set -e

BINARY="rustyschool"

if [ ! -f "$BINARY" ]; then
    echo "[-] Erro: O arquivo binário '$BINARY' não foi encontrado no diretório atual."
    echo "    Certifique-se de copiar o executável do desafio para esta pasta antes de rodar este script."
    exit 1
fi

echo "[+] Criando cópia de backup '$BINARY.bak'..."
cp "$BINARY" "$BINARY.bak"

echo "[+] Alterando a string '/dev/urandom' para './my_urandom' dentro do binário..."
python3 -c "
with open('$BINARY', 'rb') as f:
    data = f.read()
patched = data.replace(b'/dev/urandom', b'./my_urandom')
with open('$BINARY', 'wb') as f:
    f.write(patched)
"

echo "[+] Criando o arquivo simbólico fixo './my_urandom' apontando para '/dev/zero'..."
ln -sf /dev/zero my_urandom

chmod +x "$BINARY"

echo "=============================================================================="
echo "[+] Sucesso! Binário patcheado com sucesso."
echo "[+] Agora a execução em depuradores como o GDB fornecerá valores determinísticos."
echo "=============================================================================="
