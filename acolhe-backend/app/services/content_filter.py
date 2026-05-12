"""
content_filter.py
Bloqueia tentativas de troca de contato externo,
links, PIX, e conteúdo proibido.
"""

import re
from dataclasses import dataclass

@dataclass
class FilterResult:
    blocked: bool
    reason: str | None = None
    warning_to_user: str | None = None

# --- PADRÕES BLOQUEADOS ---

# Telefones
PHONE_PATTERN = re.compile(
    r'(\+?\d[\s\-.]?){8,15}|'           # número internacional
    r'\(?\d{2}\)?\s?\d{4,5}[\-\s]?\d{4}'  # formato brasileiro
)

# E-mails
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}')

# Links
URL_PATTERN = re.compile(
    r'(https?://|www\.)[^\s]+|'
    r'[a-zA-Z0-9\-]+\.(com|net|org|io|app|br|me|co)[^\s]*'
)

# Redes sociais e apps de mensagem
SOCIAL_KEYWORDS = [
    "instagram", "insta", "@", "telegram", "whatsapp", "zap",
    "discord", "snapchat", "twitter", "tiktok", "facebook",
    "signal", "skype", "zoom", "meet", "teams",
]

# PIX e dinheiro
MONEY_KEYWORDS = [
    "pix", "transferência", "transfere", "me manda", "me passa",
    "paypal", "picpay", "nubank", "banco", "conta corrente",
    "vaquinha", "financiamento", "investimento", "criptomoeda",
    "bitcoin", "dinheiro", "real", "reais", "r$",
]

# Conteúdo sexual
SEXUAL_KEYWORDS = [
    "sexo", "transar", "nudes", "foto pelado", "foto pelada",
    "pack", "conteúdo adulto", "nsfw", "putaria",
]

# Mensagens de aviso personalizadas
AVISOS = {
    "phone": "⚠️ Compartilhar contatos externos não é permitido aqui. Isso protege você.",
    "email": "⚠️ Compartilhar e-mails não é permitido. Mantenha a conversa segura.",
    "url": "⚠️ Links externos não são permitidos no Acolhe.",
    "social": "⚠️ Não compartilhe redes sociais ou apps de mensagem aqui. Isso é pela sua segurança.",
    "money": "⚠️ Qualquer pedido de dinheiro ou PIX é estritamente proibido e será denunciado.",
    "sexual": "⚠️ Conteúdo sexual não é permitido. Esta mensagem foi bloqueada.",
}

# --- FUNÇÃO PRINCIPAL ---

def filtrar_mensagem(texto: str) -> FilterResult:
    texto_lower = texto.lower()

    # Verifica telefone
    if PHONE_PATTERN.search(texto):
        return FilterResult(
            blocked=True,
            reason="phone",
            warning_to_user=AVISOS["phone"]
        )

    # Verifica e-mail
    if EMAIL_PATTERN.search(texto):
        return FilterResult(
            blocked=True,
            reason="email",
            warning_to_user=AVISOS["email"]
        )

    # Verifica links
    if URL_PATTERN.search(texto):
        return FilterResult(
            blocked=True,
            reason="url",
            warning_to_user=AVISOS["url"]
        )

    # Verifica redes sociais
    for keyword in SOCIAL_KEYWORDS:
        if keyword in texto_lower:
            return FilterResult(
                blocked=True,
                reason="social",
                warning_to_user=AVISOS["social"]
            )

    # Verifica dinheiro/PIX
    for keyword in MONEY_KEYWORDS:
        if keyword in texto_lower:
            return FilterResult(
                blocked=True,
                reason="money",
                warning_to_user=AVISOS["money"]
            )

    # Verifica conteúdo sexual
    for keyword in SEXUAL_KEYWORDS:
        if keyword in texto_lower:
            return FilterResult(
                blocked=True,
                reason="sexual",
                warning_to_user=AVISOS["sexual"]
            )

    return FilterResult(blocked=False)
