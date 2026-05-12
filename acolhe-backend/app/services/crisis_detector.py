"""
crisis_detector.py
Detecta ideação suicida, manipulação emocional e risco alto.
Retorna nível de risco e ação recomendada.
"""

from dataclasses import dataclass
from enum import Enum

class RiskLevel(str, Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class RiskResult:
    level: RiskLevel
    triggered_by: list[str]
    message_to_user: str | None = None
    message_to_listener: str | None = None
    block_message: bool = False
    show_resources: bool = False

# --- GATILHOS POR NÍVEL ---

CRITICAL_TRIGGERS = [
    "quero me matar", "vou me matar", "não quero mais viver",
    "vou acabar com tudo", "não aguento mais viver", "me machucar",
    "suicídio", "suicidar", "me suicidar", "acabar com minha vida",
    "não quero mais estar aqui", "preferia não existir",
    "vou tomar todos os remédios", "tenho uma arma",
    "não vejo saída", "melhor morto", "melhor morta",
]

HIGH_TRIGGERS = [
    "não tem sentido", "não quero mais", "cansado de tudo",
    "desaparecer", "sumir", "ninguém sentiria falta",
    "seria melhor sem mim", "não consigo mais",
    "to no limite", "não aguento mais",
]

MANIPULATION_TRIGGERS = [
    "você só precisa de mim", "não conte isso pra ninguém",
    "você é especial", "vamos sair daqui", "me manda seu contato",
    "se você sair vou me machucar", "só você me entende",
    "não fale com mais ninguém", "você me salvou",
    "sem você não consigo", "promete que fica",
]

MEDIUM_TRIGGERS = [
    "chorando muito", "não consigo parar de chorar",
    "muito sozinho", "muito sozinha", "ninguém me entende",
    "sem esperança", "sem saída", "tudo está errado",
]

# --- RECURSOS DE CRISE ---
RECURSOS_CRISE = """
🆘 *Recursos de apoio imediatos:*

• CVV — 188 (24h, gratuito)
• SAMU — 192
• CVV chat — cvv.org.br

Você não precisa passar por isso sozinho. 🫂
"""

MENSAGEM_OUVINTE = """
⚠️ A pessoa com quem você está conversando pode estar passando por um momento muito difícil.

Você não é responsável por salvar esta pessoa sozinho.
Se precisar, encerre a conversa e cuide de você também.

Recursos: CVV 188 | SAMU 192
"""

# --- FUNÇÃO PRINCIPAL ---

def analisar_mensagem(texto: str) -> RiskResult:
    texto_lower = texto.lower()

    # CRÍTICO — ideação suicida direta
    gatilhos = [t for t in CRITICAL_TRIGGERS if t in texto_lower]
    if gatilhos:
        return RiskResult(
            level=RiskLevel.CRITICAL,
            triggered_by=gatilhos,
            message_to_user=f"Percebi que você está passando por um momento muito difícil. 💙\n\n{RECURSOS_CRISE}",
            message_to_listener=MENSAGEM_OUVINTE,
            block_message=False,  # não bloqueia — deixa a pessoa falar
            show_resources=True,
        )

    # MANIPULAÇÃO
    gatilhos = [t for t in MANIPULATION_TRIGGERS if t in texto_lower]
    if gatilhos:
        return RiskResult(
            level=RiskLevel.HIGH,
            triggered_by=gatilhos,
            message_to_user="⚠️ Esta conversa foi sinalizada. Lembre-se: ninguém aqui deve ser sua única fonte de apoio.",
            block_message=False,
            show_resources=False,
        )

    # ALTO RISCO
    gatilhos = [t for t in HIGH_TRIGGERS if t in texto_lower]
    if gatilhos:
        return RiskResult(
            level=RiskLevel.HIGH,
            triggered_by=gatilhos,
            message_to_user=f"Estamos aqui com você. 🫂\n\n{RECURSOS_CRISE}",
            show_resources=True,
        )

    # MÉDIO
    gatilhos = [t for t in MEDIUM_TRIGGERS if t in texto_lower]
    if gatilhos:
        return RiskResult(
            level=RiskLevel.MEDIUM,
            triggered_by=gatilhos,
            message_to_user=None,
            show_resources=False,
        )

    return RiskResult(level=RiskLevel.SAFE, triggered_by=[])
