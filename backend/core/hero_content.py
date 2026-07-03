import re

ACCENT_PATTERN = re.compile(r'\{accent\}(.*?)\{/accent\}', re.DOTALL)
ACCENT_SPAN = (
    '<span class="bg-gradient-to-r from-amber-500 to-amber-600 '
    'bg-clip-text text-transparent">{}</span>'
)
SINGLE_P_PATTERN = re.compile(r'^<p>(.*)</p>$', re.DOTALL)


def apply_hero_placeholders(html: str, *, business_name: str, region: str) -> str:
    """Editörde kullanılan yer tutucuları güvenli şekilde doldurur."""
    if not html:
        return ''

    html = html.replace('{business_name}', business_name)
    html = html.replace('{region}', region)
    return ACCENT_PATTERN.sub(lambda m: ACCENT_SPAN.format(m.group(1)), html)


def hero_title_html(html: str, *, business_name: str, region: str) -> str:
    """H1 içine yerleştirmek için tek satırlık HTML üretir."""
    html = apply_hero_placeholders(html, business_name=business_name, region=region).strip()
    match = SINGLE_P_PATTERN.match(html)
    if match and '<p>' not in match.group(1):
        html = match.group(1)
    return html


def hero_body_html(html: str, *, business_name: str, region: str) -> str:
    """Giriş metni sütunu için paragraf HTML'i."""
    return apply_hero_placeholders(html, business_name=business_name, region=region)
