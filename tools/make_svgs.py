"""
Build the profile's SVG cards in the same style as my Internship Tracker:
pure black, Claude orange, JetBrains Mono, thin orange-tinted borders, square corners.

GitHub strips CSS from READMEs and images can't load web fonts, so each SVG
carries its own subset of JetBrains Mono as an embedded font.

    python tools/make_svgs.py        # writes assets/*.svg
"""
import base64
import io
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / 'tools' / 'fonts'
OUT = ROOT / 'assets'

BG, TEXT, MUTED = '#000000', '#f4f1ee', 'rgba(244,241,238,.55)'
EDGE, EDGE_SOFT = 'rgba(217,119,87,.32)', 'rgba(244,241,238,.14)'
ORANGE, ORANGE_TEXT = '#d97757', '#f0a58b'
PILLS = {  # the tracker's status pill colours: (text, background, border)
    'orange': ('#f0a58b', 'rgba(217,119,87,.16)', '#d97757'),
    'blue': ('#8fc2ff', 'rgba(70,140,230,.20)', '#4a8fe0'),
    'purple': ('#d4b8ff', 'rgba(150,100,230,.22)', '#9a6ae6'),
    'green': ('#9be8a8', 'rgba(60,180,90,.22)', '#3cb45a'),
    'muted': ('rgba(244,241,238,.55)', 'transparent', 'rgba(244,241,238,.14)'),
}
W = 840          # card width; GitHub scales it to the column
ADV = 0.6        # JetBrains Mono advance width, in em


def text_width(s, size):
    return len(s) * ADV * size


def font_css(text):
    """@font-face rules with JetBrains Mono subset to the characters used."""
    chars = ''.join(sorted(set(text + ' >_▍·↗')))
    rules = []
    for weight, name in [(400, 'JetBrainsMono-Regular.ttf'), (600, 'JetBrainsMono-SemiBold.ttf')]:
        font = TTFont(FONTS / name)
        opts = subset.Options()
        opts.layout_features = []          # no ligatures
        opts.name_IDs = ['*']
        sub = subset.Subsetter(opts)
        sub.populate(text=chars)
        sub.subset(font)
        buf = io.BytesIO()
        font.save(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        rules.append(f"@font-face{{font-family:'JBM';font-weight:{weight};"
                     f"src:url(data:font/ttf;base64,{b64}) format('truetype');}}")
    return ''.join(rules)


def svg(height, body, label, all_text):
    css = (font_css(all_text) +
           f"text{{font-family:'JBM',ui-monospace,'SF Mono',Menlo,Consolas,monospace;"
           f"font-variant-ligatures:none;fill:{TEXT};}}"
           f".m{{fill:{MUTED};}}.o{{fill:{ORANGE};}}.ot{{fill:{ORANGE_TEXT};}}.b{{font-weight:600;}}"
           "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.cur{animation:blink 1.1s step-end infinite;}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
            f'role="img" aria-label="{escape(label)}"><title>{escape(label)}</title><style>{css}</style>'
            f'<rect x=".5" y=".5" width="{W - 1}" height="{height - 1}" fill="{BG}" stroke="{EDGE}"/>'
            f'{body}</svg>')


def t(x, y, s, size, cls='', anchor='start'):
    c = f' class="{cls}"' if cls else ''
    a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
    return f'<text x="{x}" y="{y}" font-size="{size}"{c}{a} xml:space="preserve">{escape(s)}</text>'


def heading(x, y, s, size=15):
    """'> heading' with an orange prompt, like the tracker's h1."""
    return t(x, y, '>', size, 'o b') + t(x + text_width('> ', size), y, s, size, 'b')


def pill(x, y, s, colour='orange', size=12, pad=10, h=24):
    fg, bg, border = PILLS[colour]
    w = text_width(s, size) + 2 * pad
    shape = (f'<rect x="{x + .5}" y="{y + .5}" width="{w - 1}" height="{h - 1}" fill="{bg}" stroke="{border}"'
             + (' stroke-dasharray="3 2"' if colour == 'muted' else '') + '/>')
    label = f'<text x="{x + pad}" y="{y + h / 2 + size * 0.36}" font-size="{size}" style="fill:{fg}">{escape(s)}</text>'
    return shape + label, w


# ------------------------------------------------------------------ cards
def header():
    name, line2, line3 = 'Krish Ahir', 'BSc Statistics @ UCL · London', \
        'risk modelling · quantitative finance · statistical computing'
    body = (t(36, 74, '>', 36, 'o b') + t(36 + text_width('> ', 36), 74, name, 36, 'b')
            + f'<rect class="cur" x="{36 + text_width("> " + name + " ", 36)}" y="46" width="14" height="34" fill="{ORANGE}"/>'
            + t(38, 116, line2, 16)
            + t(38, 146, line3, 13.5, 'm'))
    return svg(184, body, f'{name}. {line2}. {line3}.', name + line2 + line3)


def about():
    # (bullet, text): a blank bullet continues the line above
    lines = [
        ('·', 'First-year BSc Statistics student at UCL (2026–29).'),
        ('·', 'Interested in market risk, volatility modelling and'),
        (' ', 'turning messy data into clear decisions.'),
        ('·', 'First-Year Rep (Research), UCL Data Science Society.'),
        ('·', 'IPQ research: can intraday trading be called gambling?'),
    ]
    body = heading(32, 44, 'about')
    y = 82
    for bullet, line in lines:
        body += t(34, y, bullet, 13.5, 'ot') + t(56, y, line, 13.5)
        y += 26
    text = ' '.join(line for _, line in lines)
    return svg(y + 8, body, 'About: ' + text, 'about' + text)


def stack():
    rows = [
        ('languages', [('Python', 'orange'), ('R', 'orange'), ('LaTeX', 'orange')]),
        ('libraries', [('NumPy', 'blue'), ('pandas', 'blue'), ('SciPy', 'blue'),
                       ('arch', 'blue'), ('matplotlib', 'blue'), ('yfinance', 'blue')]),
        ('tools', [('Git', 'purple'), ('VS Code', 'purple'), ('Cursor', 'purple'), ('Jupyter', 'purple')]),
        ('speaks', [('English', 'muted'), ('Spanish', 'muted')]),
    ]
    body = heading(32, 44, 'stack')
    y = 70
    for label, items in rows:
        body += t(34, y + 17, label, 12.5, 'm')
        x = 160
        for name, colour in items:
            p, w = pill(x, y, name, colour)
            body += p
            x += w + 8
        y += 36
    all_text = 'stack' + ''.join(l + ''.join(n for n, _ in i) for l, i in rows)
    label = 'Stack: ' + '; '.join(f"{l}: {', '.join(n for n, _ in i)}" for l, i in rows)
    return svg(y + 14, body, label, all_text)


def featured(name, desc, tags, pills, label):
    """'> featured' card holding one project, drawn like one row of the tracker."""
    top = 64                         # the row starts below the heading
    body = heading(32, 44, 'featured')
    body += f'<rect x="28.5" y="{top + .5}" width="{W - 57}" height="111" fill="{BG}" stroke="{EDGE}"/>'
    body += t(48, top + 34, name, 17, 'b') + t(W - 48, top + 34, '↗', 17, 'ot', 'end')
    body += t(48, top + 60, desc, 13)
    x = 48
    for s, colour in pills:
        p, w = pill(x, top + 76, s, colour, size=11.5, pad=9, h=22)
        body += p
        x += w + 8
    body += t(x + 6, top + 92, tags, 12, 'm')
    all_text = 'featured' + name + desc + tags + ''.join(s for s, _ in pills)
    return svg(top + 140, body, label, all_text)


def connect(text, label):
    """'> connect' card with one link button (the whole image is the link)."""
    size, pad = 13, 16
    w = text_width(text, size) + 2 * pad + 18
    body = heading(32, 44, 'connect')
    body += (f'<rect x="32.5" y="64.5" width="{w - 1}" height="35" fill="{BG}" stroke="{EDGE_SOFT}"/>'
             + t(32 + pad, 82 + size * .36, text, size)
             + t(32 + w - pad, 82 + size * .36, '↗', size, 'ot', 'end'))
    return svg(124, body, label, 'connect' + text)


def var_banner():
    title, sub = 'value-at-risk', 'How much can a 5-stock portfolio lose in a day, and how often is the model wrong?'
    meta = 'historical · normal · Monte Carlo · GARCH(1,1) · Kupiec & Christoffersen backtests'
    body = (t(36, 70, '>', 32, 'o b') + t(36 + text_width('> ', 32), 70, title, 32, 'b')
            + t(38, 110, sub, 13.5) + t(38, 140, meta, 12, 'm'))
    return svg(176, body, f'{title}: {sub}', title + sub + meta)


def main():
    OUT.mkdir(exist_ok=True)
    files = {
        'header.svg': header(),
        'about.svg': about(),
        'stack.svg': stack(),
        'featured.svg': featured(
            'value-at-risk',
            'One-day VaR for a 5-stock portfolio, backtested on the April 2025 tariff sell-off.',
            'NumPy · pandas · arch',
            [('Python', 'orange'), ('risk', 'blue'), ('GARCH', 'purple')],
            'Featured project, value-at-risk: one-day VaR for a 5-stock portfolio, '
            'backtested on the April 2025 tariff sell-off.'),
        'connect.svg': connect('LinkedIn', 'Connect on LinkedIn: krish-ahir'),
        'var-banner.svg': var_banner(),
    }
    for name, content in files.items():
        (OUT / name).write_text(content, encoding='utf-8')
        print(f'{name:18} {len(content) / 1024:6.1f} KB')


if __name__ == '__main__':
    main()
