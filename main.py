import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any

from analyzer import analyze_image
from namer import generate_name


def format_verbose_output(features: Dict[str, Any], debug_info: Dict[str, Any], name: str) -> str:
    lines = [
        "=== ANÁLISE DA IMAGEM ===",
        f"Dimensões: {features['width']}x{features['height']}",
        f"Proporção: {features['aspect_ratio']:.2f} ({features['orientation']})",
        f"Brilho: {features['brightness']:.2%} ({features['brightness_category']})",
        f"Cores dominantes: {', '.join(features['color_names'][:5])}",
        "",
        "=== GATILHOS IDENTIFICADOS ===",
        f"Cores: {', '.join(debug_info.get('color_triggers', [])) or 'nenhum'}",
        f"Orientação: {', '.join(debug_info.get('orientation_triggers', [])) or 'nenhum'}",
        f"Brilho: {', '.join(debug_info.get('brightness_triggers', [])) or 'nenhum'}",
        f"Proporção: {', '.join(debug_info.get('aspect_triggers', [])) or 'nenhum'}",
        "",
        "=== SELEÇÃO DETERMINÍSTICA ===",
        f"Seed: {debug_info.get('seed', 'N/A')}",
        f"Substantivo base: {debug_info.get('selected_noun', 'N/A')}",
        f"Adjetivo base: {debug_info.get('selected_adj', 'N/A')}",
        f"Conector: '{debug_info.get('connector', '')}' (usado: {debug_info.get('use_connector', False)})",
        f"Segundo adjetivo: {'sim' if debug_info.get('use_second_adj', False) else 'não'}",
        "",
        f"=== RESULTADO ===",
        f"Nome: {name}",
    ]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Gera nomes surreais/desconexos baseados em análise de pixels e metadados EXIF de imagens.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python -m main foto.jpg
  python -m main foto.jpg --verbose
  python -m main foto.jpg --json
  python -m main foto.jpg --verbose --json
        """
    )
    parser.add_argument("image", help="Caminho para o arquivo de imagem")
    parser.add_argument("-v", "--verbose", action="store_true", help="Exibe a lógica detalhada da escolha do nome")
    parser.add_argument("-j", "--json", action="store_true", help="Retorna o resultado em formato JSON")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Erro: Arquivo não encontrado: {args.image}", file=sys.stderr)
        sys.exit(1)
    if not image_path.is_file():
        print(f"Erro: Não é um arquivo: {args.image}", file=sys.stderr)
        sys.exit(1)

    try:
        features = analyze_image(str(image_path))
        name, debug_info = generate_name(features, verbose=args.verbose)

        if args.json:
            result = {
                "name": name,
                "image": str(image_path),
                "features": {
                    "width": features["width"],
                    "height": features["height"],
                    "aspect_ratio": round(features["aspect_ratio"], 4),
                    "orientation": features["orientation"],
                    "brightness": round(features["brightness"], 4),
                    "brightness_category": features["brightness_category"],
                    "dominant_colors": features["color_names"][:5],
                }
            }
            if args.verbose:
                result["debug"] = debug_info
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.verbose:
            print(format_verbose_output(features, debug_info, name))
        else:
            print(name)
    except Exception as e:
        print(f"Erro ao processar imagem: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()