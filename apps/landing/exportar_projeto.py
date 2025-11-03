import os

# --- CONFIGURAÇÕES DO SCRIPT ---

# Pasta onde o script será executado. "." significa a pasta atual.
PASTA_BASE = "."

# Lista de extensões de arquivo que devem ser incluídas na exportação.
EXTENSOES = [
    # Código e Componentes
    ".tsx", ".ts", ".jsx", ".js",
    # Estilos
    ".css",
    # Estrutura e Configuração
    ".html", ".json",
    # Assets relevantes
    ".svg"
]

# Conjunto de nomes de pastas a serem completamente ignoradas.
EXCLUIR_PASTAS = {
    # Pastas de dependências e builds
    "node_modules",
    "dist",
    "build",
    ".next",
    # Pastas de controle de versão e sistema
    ".git",
    # Pasta de assets estáticos (geralmente não contém lógica)
    "public",
    # Específicos de Python (para manter a versatilidade)
    "__pycache__", ".venv", "venv"
}

# Lista de nomes de arquivos específicos a serem ignorados.
EXCLUIR_ARQUIVOS = {
    "package-lock.json",
    "yarn.lock",
}

# --- LÓGICA DE EXPORTAÇÃO ---

saida = []

print("🔎 Iniciando varredura do projeto...")

for root, dirs, files in os.walk(PASTA_BASE, topdown=True):
    # Remove as pastas indesejadas da lista de diretórios a serem percorridos
    dirs[:] = [d for d in dirs if d not in EXCLUIR_PASTAS and not d.startswith('.')]

    for file in files:
        # Verifica se o arquivo não deve ser excluído e se tem a extensão desejada
        if file in EXCLUIR_ARQUIVOS:
            continue
        
        if any(file.endswith(ext) for ext in EXTENSOES):
            caminho_completo = os.path.join(root, file)
            caminho_relativo = os.path.relpath(caminho_completo, start=PASTA_BASE)

            # Ignora arquivos dentro de pastas ocultas que não foram excluídas antes
            if any(part.startswith('.') for part in caminho_relativo.split(os.sep)):
                continue

            try:
                with open(caminho_completo, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                
                # Adiciona ao output formatado
                saida.append(f"📄 {caminho_relativo}\n---\n{conteudo}\n---\n")
                print(f"  -> Exportado: {caminho_relativo}")

            except Exception as e:
                print(f"  -> ⚠️  Erro ao ler o arquivo {caminho_relativo}: {e}")

# Escreve o resultado em um único arquivo de texto
try:
    with open("export_projeto.txt", "w", encoding="utf-8") as f_out:
        f_out.writelines(saida)
    print("\n✅ Projeto exportado com sucesso para 'export_projeto.txt'")
except Exception as e:
    print(f"\n❌ Erro ao salvar o arquivo final: {e}")