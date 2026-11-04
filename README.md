# Surreal-namer

> **Nota de Desenvolvimento:** Este projeto foi desenvolvido predominantemente com o auxílio de **Inteligência Artificial** (agentes de IA e modelos de linguagem), englobando desde a concepção do algoritmo determinístico de processamento visual até a construção das interfaces CLI/GUI, suíte de testes unitários e documentação[cite: 4, 6, 28].

O **surreal-namer** é um gerador determinístico em Python que analisa imagens (pixels e metadados EXIF) para criar nomes surreais e desconexos (ex: *"Botão crepuscular"*)[cite: 4, 5].

A aplicação mede a paleta de cores dominantes, a luminosidade média e a proporção do arquivo para derivar uma *seed* única via *hash* MD5[cite: 6, 7, 8, 9, 15, 16]. Essa *seed* seleciona combinações de palavras em português de forma 100% reprodutível[cite: 5, 11, 18].

---

## Funcionalidades

- **Determinismo Total:** A mesma imagem gerará sempre o mesmo nome em qualquer execução ou sistema, sem necessidade de banco de dados[cite: 5].
- **Análise Visual Avançada:**
  * Mapeamento de cores dominantes em espaço HSV via algoritmo *MEDIANCUT*[cite: 7, 8].
  * Cálculo de brilho e classificação de orientação (horizontal, vertical, quadrada, ultra-wide)[cite: 8, 9, 10].
  * Leitura informativa de metadados EXIF[cite: 7, 10].
- **Duas Interfaces Integradas:**
  * **CLI (`main.py`):** Para utilização via terminal ou integração em rotinas de automação (com saída em texto limpo ou JSON)[cite: 4, 24].
  * **GUI (`gui.py`):** Interface visual desenvolvida em PyQt6 com suporte a *drag-and-drop*, pré-visualização, temas claro/escuro e processamento em *thread* separada[cite: 4, 26].
- **Auditoria Detalhada:** Suporte ao modo `--verbose` para visualizar as características extraídas, gatilhos acionados e a matemática por trás da escolha do nome[cite: 24, 25].

---

## Como Funciona

1. **Extração (`analyzer.py`):** Reduz a imagem a uma miniatura para calcular as cores mais frequentes, normaliza a luminância e mede a proporção da tela[cite: 7, 8, 9].
2. **Geração de Seed (`namer.py`):** As métricas são formatadas numa cadeia de texto e processadas por um *hash* MD5[cite: 15, 16]. Os primeiros 8 dígitos hexadecimais convertem-se num inteiro de 32 bits[cite: 16].
3. **Seleção Determinística:** O valor da *seed* mapeia posições em tuplas de substantivos e adjetivos (acrescentados de gatilhos visuais)[cite: 11, 13, 18, 20].

Leia a documentação na pasta **Documentação** do projeto para entender mais a fundo como o programa funciona.

---

## Estrutura do Projeto

```text
surreal-namer/
├── analyzer.py          # Extração de métricas de pixels e metadados EXIF
├── namer.py             # Algoritmo de geração determinística e vocabulário
├── main.py              # Ponto de entrada da CLI
├── gui.py               # Interface gráfica em PyQt6
├── build_exe.py         # Script de automação do PyInstaller
├── build.spec           # Arquivo de especificação do build
├── requirements.txt     # Dependências de execução (Pillow, PyQt6)
├── test_analyzer.py     # Suite de testes para o analisador
└── test_namer.py        # Suite de testes para o gerador de nomes
