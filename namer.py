import hashlib
from typing import Dict, List, Tuple, Any

SUBSTANTIVOS = (
    "melão", "abacaxi", "tangerina", "jabuticaba", "pitanga", "cajá", "umbu",
    "cactus", "samambaia", "bromélia", "orquídea", "violetas", "girassol",
    "tijolo", "telha", "cimento", "areia", "cal", "argamassa", "ladrilho",
    "garfo", "colher", "faca", "prato", "xícara", "pires", "panela",
    "meia", "chinelo", "cadarço", "botão", "zíper", "bolso", "gola",
    "prego", "parafuso", "porca", "arruela", "martelo", "chave", "serra",
    "nuvem", "névoa", "orvalho", "geada", "granizo", "chuvisco", "arco-íris",
    "formiga", "besouro", "borboleta", "libélula", "grilo", "cigarra", "mosca",
    "cadeira", "mesa", "sofá", "estante", "tapete", "cortina", "almofada",
    "relógio", "bússola", "mapa", "lente", "espelho", "óculos", "binóculo",
    "violino", "flauta", "tambor", "pandeiro", "triângulo", "chocalho", "berimbau",
    "caderno", "lápis", "borracha", "apontador", "régua", "esquadro", "compassos",
    "botina", "galocha", "sapatilha", "mocassim", "tênis", "sandália", "ralaste",
    "guarda-chuva", "guarda-sol", "capa", "poncho", "blusa", "casaco", "jaqueta",
    "travesseiro", "lençol", "cobertor", "edredom", "fronha", "colcha", "manta",
    "chaveiro", "cordão", "pulseira", "anel", "brinco", "colar", "broche",
    "vassoura", "rodo", "balde", "espanador", "pá", "enxada", "ancinho",
    "janela", "porta", "fechadura", "dobradiça", "batente", "soleira", "peitoril",
    "geladeira", "fogão", "forno", "micro-ondas", "liquidificador", "batedeira", "torradeira",
    "ônibus", "bonde", "metrô", "trem", "barca", "balsa", "gôndola",
    "farol", "boia", "âncora", "leme", "vela", "mastro", "convés",
    "farinha", "açúcar", "sal", "fermento", "ovos", "leite", "manteiga",
    "bigorna", "tenaz", "formão", "goiva",
    "agulha", "linha", "dedal", "novelo", "carretel", "fita",
    "carimbo", "pena", "pergaminho", "selo", "envelope", "carta",
    "lanterna", "fosforo", "isqueiro", "pavio", "cera", "goteira",
    "balão", "pipa", "catavento", "bolha", "pião", "peteca", "bexiga",
    "guardanapo", "toalha", "passadeira", "capacho", "esteira", "tatame",
    "berço", "carrinho", "andador", "cadeirinha", "bebê-conforto", "moisés", "cercadinho",
    "café", "chá", "suco", "água", "refrigerante", "cerveja",
    "pão", "bolo", "torta", "biscoito", "bolacha", "rosca", "sonho",
    "praia", "mar", "rio", "lago", "cachoeira", "fonte", "nascentes",
    "montanha", "morro", "colina", "vale", "planície", "platô", "vulcão",
    "estrela", "planeta", "lua", "sol", "cometa", "asteroide", "galáxia",
    "raiz", "tronco", "galho", "folha", "flor", "fruto", "semente",
    "osso", "dente", "unha", "cabelo", "pele", "sangue", "músculo",
    "pesadelo", "devaneio", "ideia", "pensamento", "memória", "esquecimento",
    "vento", "brisa", "rajada", "vendaval", "furacão", "tornado", "ciclone",
    "pedra", "rocha", "seixo", "cascalho", "pó", "lama",
    "fogo", "brasa", "cinza", "fumaça", "faísca", "chama", "labareda",
    "ouro", "prata", "bronze", "cobre", "ferro", "aço", "chumbo",
    "seda", "algodão", "lã", "linho", "couro", "pelúcia", "veludo",
    "vinho", "vinagre", "azeite", "mel", "geleia", "doce", "compota",
    "livro", "revista", "jornal", "gib quadrinho", "manual", "guia",
    "caneta", "marcador", "grafite", "pincel", "tela",
    "fone", "caixa", "cabo", "plug", "tomada", "interruptor", "lâmpada",
    "teclado", "mouse", "monitor", "cpu", "hd", "placa-mãe",
    "gelo", "neve", "chuva",
)

ADJETIVOS = (
    "flamenguista", "vascaíno", "tricolor", "alviverde", "santista", "corintiano", "gremista",
    "sonolento", "acordado", "desperto", "adormecido", "vigilante", "distraído", "atento",
    "felpudo", "liso", "áspero", "macio", "duro", "mole", "escorregadio",
    "barulhento", "silencioso", "sussurrante", "estridente", "melodioso", "dissonante", "mudo",
    "quente", "frio", "morna", "gelada", "escaldante", "congelante", "tépida",
    "lento", "rápido", "devagar", "apressado", "parado", "em movimento", "estático",
    "leve", "pesado", "pena", "chumbo", "flutuante", "afundando", "pairando",
    "brilhante", "opaco", "fosco", "lustroso", "mate", "cintilante", "embaçado",
    "doce", "amargo", "azedo", "salgado", "picante", "insosso", "temperado",
    "redondo", "quadrado", "triangular", "oval", "retangular", "hexagonal", "informes",
    "novo", "velho", "antigo", "moderno", "futurista", "arcaico", "atemporal",
    "grande", "pequeno", "iminuto", "gigante", "microscópico", "colossal", "médio",
    "longe", "perto", "distante", "próximo", "adjacente", "remoto", "íntimo",
    "alto", "baixo", "rasteiro", "elevado", "suspenso", "pendente",
    "seco", "úmido", "molhado", "encharcado", "secando", "evaporando", "condensando",
    "limpo", "sujo", "imaculado", "manchado", "puro", "contaminado", "higiênico",
    "cheiroso", "fedorento", "perfumado", "inodoro", "aromático", "rançoso", "fresco",
    "colorido", "monocromático", "vibrante", "pálido", "intenso", "desbotado", "neon",
    "rígido", "flexível", "quebradiço", "elástico", "plástico", "frágil",
    "vivo", "morto", "inanimado", "animado", "respirando", "pulsando",
    "livre", "preso", "solto", "amarrado", "enjaulado", "escravo", "autônomo",
    "rico", "pobre", "abastado", "miserável", "opulento", "escasso", "farto",
    "triste", "alegre", "melancólico", "eufórico", "sereno", "agitado", "calmo",
    "forte", "fraco", "poderoso", "robusto", "delicado", "resistente",
    "sábio", "tolo", "inteligente", "burro", "genial", "medíocre",
    "jovem", "idoso", "ancião", "criança", "adolescente", "adulto", "eterno",
    "útil", "inútil", "funcional", "defeituoso", "quebrado", "inteiro", "perfeito",
    "simples", "complexo", "básico", "avançado", "primitivo", "sofisticado", "elementar",
    "comum", "raro", "único", "extraordinário", "excepcional", "singular", "plural",
    "suave", "violento", "brando", "gentil",
    "claro", "escuro", "luminoso", "sombrio", "radiantes", "tenebroso", "crepuscular",
    "árido", "pantanoso", "desértico", "tropical",
    "pontiagudo", "afiado", "cego", "curvo", "reto", "torto",
    "falso", "verdadeiro", "real", "imaginário", "ilusório", "concreto", "abstrato",
    "movimento", "dinâmico", "cinético", "potencial", "inercial",
    "aberto", "fechado", "entreaberto", "trancado", "destrancado", "selado", "lacrado",
    "cheio", "vazio", "lotado", "deserto", "povoado", "habitado", "abandonado",
    "usado", "gasto", "novo em folha", "segunda mão", "vintage", "retro",
)

COLOR_TRIGGERS: Dict[str, Tuple[str, ...]] = {
    "vermelho": ("flamenguista", "corintiano", "rubro-negro", "sangrento", "incandescente"),
    "preto": ("noturno", "sombrio", "obsidiano", "ebano", "carbonizado"),
    "branco": ("alvo", "neve", "leitoso", "perolado", "marfim"),
    "azul": ("tricolor", "vascaíno", "oceânico", "celeste", "safira"),
    "verde": ("alviverde", "gremista", "esmeralda", "musgoso", "florestal"),
    "amarelo": ("canarinho", "dourado", "âmbar", "citrino", "solar"),
    "laranja": ("tangerina", "abóbora", "ferrugem", "âmbar", "crepuscular"),
    "roxo": ("amethista", "violeta", "real", "imperial", "místico"),
    "rosa": ("quartzo", "rosado", "corado", "ruborizado", "delicado"),
    "cinza": ("chumbo", "prateado", "cinzento", "nevoento", "metálico"),
    "marrom": ("terra", "café", "chocolate", "caramelo", "castanho"),
}

ORIENTATION_TRIGGERS: Dict[str, Tuple[str, ...]] = {
    "vertical": ("tijolo", "torre", "coluna", "obelisco", "totem", "monolito"),
    "horizontal": ("tapete", "esteira", "trilho", "ponte", "passarela", "corredor"),
    "quadrada": ("quadro", "azulejo", "ladrilho", "dado", "cubo", "bloco"),
}

BRIGHTNESS_TRIGGERS: Dict[str, Tuple[str, ...]] = {
    "escura": ("noturno", "sombrio", "obscuro", "tenebroso", "negro", "eclipsado"),
    "clara": ("luminoso", "radiante", "ofuscante", "esplendente", "brilhante", "solar"),
    "media": ("penumbra", "crepuscular", "meia-luz", "suave", "moderado", "equilibrado"),
}

ASPECT_TRIGGERS: Dict[str, Tuple[str, ...]] = {
    "ultra_wide": ("panorâmico", "cinemascope", "letterbox", "widescreen", "alongado"),
    "wide": ("retangular", "alongado", "estendido", "comprido", "horizontal"),
    "tall": ("vertical", "alto", "estirado", "alongado", "torre"),
    "square": ("quadrado", "perfeito", "simétrico", "equilibrado", "geométrico"),
}


def get_seed_from_features(features: Dict[str, Any]) -> int:
    color_str = "".join(features.get("color_names", [])[:5])
    brightness_str = f"{features.get('brightness', 0):.4f}"
    aspect_str = f"{features.get('aspect_ratio', 1):.4f}"
    size_str = f"{features.get('width', 0)}x{features.get('height', 0)}"
    seed_string = f"{color_str}|{brightness_str}|{aspect_str}|{size_str}"
    hash_obj = hashlib.md5(seed_string.encode())
    return int(hash_obj.hexdigest()[:8], 16)


def select_from_list(lst: Tuple[str, ...], seed: int, index: int) -> str:
    return lst[(seed + index * 1009) % len(lst)]


def get_color_triggers(color_names: List[str]) -> List[str]:
    triggers = []
    for color in color_names[:3]:
        triggers.extend(COLOR_TRIGGERS.get(color, ()))
    return triggers


def get_orientation_triggers(orientation: str) -> List[str]:
    return list(ORIENTATION_TRIGGERS.get(orientation, ()))


def get_brightness_triggers(brightness_cat: str) -> List[str]:
    return list(BRIGHTNESS_TRIGGERS.get(brightness_cat, ()))


def get_aspect_triggers(aspect_ratio: float) -> List[str]:
    if aspect_ratio > 2.0:
        return list(ASPECT_TRIGGERS["ultra_wide"])
    elif aspect_ratio > 1.3:
        return list(ASPECT_TRIGGERS["wide"])
    elif aspect_ratio < 0.5:
        return list(ASPECT_TRIGGERS["tall"])
    elif aspect_ratio < 0.77:
        return list(ASPECT_TRIGGERS["tall"])
    return list(ASPECT_TRIGGERS["square"])


def generate_name(features: Dict[str, Any], verbose: bool = False) -> Tuple[str, Dict[str, Any]]:
    seed = get_seed_from_features(features)
    color_triggers = get_color_triggers(features.get("color_names", []))
    orientation_triggers = get_orientation_triggers(features.get("orientation", "quadrada"))
    brightness_triggers = get_brightness_triggers(features.get("brightness_category", "media"))
    aspect_triggers = get_aspect_triggers(features.get("aspect_ratio", 1.0))
    noun_pool = SUBSTANTIVOS + tuple(orientation_triggers) + tuple(aspect_triggers)
    adj_pool = ADJETIVOS + tuple(color_triggers) + tuple(brightness_triggers)
    noun = select_from_list(noun_pool, seed, 0)
    adj = select_from_list(adj_pool, seed + 1, 1)
    use_connector = (seed + 2) % 3 == 0
    use_second_adj = (seed + 3) % 4 == 0
    connectors = (" ", " de ", " do ", " da ", " e ", " com ")
    connector = select_from_list(connectors, seed + 4, 2) if use_connector else " "
    name_parts = [noun]
    if use_second_adj:
        adj2 = select_from_list(adj_pool, seed + 5, 3)
        name_parts.append(connector + adj2)
    name_parts.append(connector + adj)
    name = "".join(name_parts).strip()
    name = name[0].upper() + name[1:] if name else "Sem Nome"
    debug_info = {
        "seed": seed,
        "color_triggers": color_triggers,
        "orientation_triggers": orientation_triggers,
        "brightness_triggers": brightness_triggers,
        "aspect_triggers": aspect_triggers,
        "selected_noun": noun,
        "selected_adj": adj,
        "use_connector": use_connector,
        "use_second_adj": use_second_adj,
        "connector": connector if use_connector else None,
    } if verbose else {}
    return name, debug_info