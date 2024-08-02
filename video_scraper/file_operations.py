def save_to_file(data, filename):
    """Salva os dados em um arquivo."""
    with open(filename, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(str(item) + '\n')
    print(f"Dados salvos no arquivo {filename}")
