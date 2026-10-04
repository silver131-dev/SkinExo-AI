"""Presentation-only design tokens for the SkinExo-AI Explorer.

This module contains no data access, scientific classification, or retrieval logic.
"""

from __future__ import annotations


COLORS = {
    "pearl_white": "#F7F5F1",
    "warm_ivory": "#EFEAE2",
    "soft_blush": "#EEDDD9",
    "mist_mint": "#DDEBE5",
    "powder_aqua": "#DCE9EC",
    "pale_lavender": "#E8E2EE",
    "champagne": "#D9C8AE",
    "deep_ink": "#173033",
}

SPACING = {
    "xs": "0.35rem",
    "sm": "0.65rem",
    "md": "1rem",
    "lg": "1.5rem",
    "xl": "2.25rem",
    "xxl": "3.5rem",
}

RADII = {
    "sm": "10px",
    "md": "16px",
    "lg": "24px",
    "pill": "999px",
}

SHADOWS = {
    "soft": "0 12px 38px rgba(23, 48, 51, 0.07)",
    "lifted": "0 18px 54px rgba(23, 48, 51, 0.11)",
    "focus": "0 0 0 3px rgba(217, 200, 174, 0.30)",
}

TYPOGRAPHY = {
    "sans": '"Inter", "Avenir Next", "Segoe UI", "Noto Sans", sans-serif',
    "display": '"Avenir Next", "Inter", "Segoe UI", "Noto Sans", sans-serif',
    "mono": '"SFMono-Regular", Consolas, "Liberation Mono", monospace',
    "hero_size": "clamp(2.7rem, 6vw, 4.9rem)",
    "section_size": "clamp(1.35rem, 2.4vw, 2rem)",
    "body_size": "1rem",
}

TRANSITIONS = {
    "standard": "720ms cubic-bezier(0.22, 1, 0.36, 1)",
    "slow": "880ms cubic-bezier(0.22, 1, 0.36, 1)",
}


def explorer_css() -> str:
    """Return the offline CSS theme used by the Streamlit presentation layer."""

    c = COLORS
    return f"""
<style>
  :root {{
    --pearl-white: {c['pearl_white']};
    --warm-ivory: {c['warm_ivory']};
    --soft-blush: {c['soft_blush']};
    --mist-mint: {c['mist_mint']};
    --powder-aqua: {c['powder_aqua']};
    --pale-lavender: {c['pale_lavender']};
    --champagne: {c['champagne']};
    --deep-ink: {c['deep_ink']};
    --line: rgba(23, 48, 51, 0.16);
    --line-strong: rgba(23, 48, 51, 0.30);
    --glass: rgba(247, 245, 241, 0.78);
    --transition: {TRANSITIONS['standard']};
  }}

  html, body, [class*="css"], [data-testid="stAppViewContainer"] {{
    font-family: {TYPOGRAPHY['sans']};
    color: var(--deep-ink);
  }}

  [data-testid="stAppViewContainer"] {{
    background:
      radial-gradient(circle at 8% 2%, rgba(238, 221, 217, 0.58), transparent 29rem),
      radial-gradient(circle at 94% 12%, rgba(220, 233, 236, 0.70), transparent 32rem),
      linear-gradient(155deg, var(--pearl-white) 0%, #faf9f6 58%, var(--warm-ivory) 100%);
  }}

  [data-testid="stHeader"] {{
    background: rgba(247, 245, 241, 0.78);
    backdrop-filter: blur(18px);
    border-bottom: 1px solid rgba(23, 48, 51, 0.07);
  }}

  .block-container {{
    max-width: 1380px;
    padding-top: 4.5rem;
    padding-bottom: 4.5rem;
  }}

  h1, h2, h3, h4, [data-testid="stHeadingWithActionElements"] {{
    font-family: {TYPOGRAPHY['display']};
    color: var(--deep-ink);
    letter-spacing: -0.025em;
  }}

  h1 {{
    font-size: {TYPOGRAPHY['hero_size']} !important;
    line-height: 0.98 !important;
    letter-spacing: -0.055em !important;
    margin: 0.15rem 0 0.55rem !important;
  }}

  h2 {{ margin-top: 1.45rem !important; }}
  p, li, label {{ color: var(--deep-ink); }}

  .skinexo-hero {{
    position: relative;
    overflow: hidden;
    padding: 1.35rem 1.55rem 1.45rem;
    margin-bottom: 0.5rem;
    border: 1px solid rgba(23, 48, 51, 0.12);
    border-radius: {RADII['lg']};
    background: linear-gradient(120deg, rgba(247,245,241,0.92), rgba(221,235,229,0.62));
    box-shadow: {SHADOWS['soft']};
    backdrop-filter: blur(20px);
  }}

  .skinexo-hero::after {{
    content: "";
    position: absolute;
    width: 12rem;
    height: 12rem;
    right: -4rem;
    top: -5rem;
    border: 1px solid rgba(217, 200, 174, 0.65);
    border-radius: 50%;
    box-shadow: inset 0 0 0 1.5rem rgba(232, 226, 238, 0.16);
    pointer-events: none;
  }}

  .skinexo-eyebrow, .section-kicker {{
    color: var(--deep-ink);
    font-size: 0.72rem;
    font-weight: 760;
    letter-spacing: 0.16em;
    text-transform: uppercase;
  }}

  .skinexo-subtitle {{
    max-width: 880px;
    margin: 0.1rem 0 0.45rem;
    font-size: clamp(1.25rem, 2.5vw, 2rem);
    font-weight: 590;
    line-height: 1.12;
  }}

  .skinexo-support {{
    max-width: 820px;
    color: rgba(23, 48, 51, 0.78);
    font-size: 1.02rem;
    line-height: 1.65;
  }}

  .skinexo-principle {{
    display: inline-flex;
    align-items: center;
    gap: 0.55rem;
    margin-top: 0.75rem;
    padding: 0.45rem 0.75rem;
    border-radius: {RADII['pill']};
    background: rgba(232, 226, 238, 0.68);
    border: 1px solid rgba(23, 48, 51, 0.12);
    font-size: 0.82rem;
    font-weight: 650;
  }}

  div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: var(--glass);
    border: 1px solid var(--line) !important;
    border-radius: {RADII['md']} !important;
    box-shadow: {SHADOWS['soft']};
    backdrop-filter: blur(16px);
    transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
  }}

  div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
    border-color: rgba(217, 200, 174, 0.88) !important;
    box-shadow: {SHADOWS['lifted']};
  }}

  [data-testid="stMetric"] {{
    min-height: 7.2rem;
    padding: 0.95rem 1rem;
    border: 1px solid var(--line);
    border-radius: {RADII['md']};
    background: rgba(247, 245, 241, 0.76);
  }}

  [data-testid="stMetricLabel"] {{
    font-size: 0.72rem;
    font-weight: 730;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}

  [data-testid="stMetricValue"] {{
    color: var(--deep-ink);
    font-size: 1.03rem;
    font-weight: 620;
    line-height: 1.32;
    white-space: normal;
  }}

  [data-baseweb="tab-list"] {{
    gap: 0.35rem;
    padding: 0.25rem;
    background: rgba(239, 234, 226, 0.70);
    border: 1px solid var(--line);
    border-radius: {RADII['pill']};
  }}

  [data-baseweb="tab"] {{
    border-radius: {RADII['pill']};
    color: var(--deep-ink);
    font-weight: 650;
    transition: background var(--transition);
  }}

  [aria-selected="true"][data-baseweb="tab"] {{
    background: rgba(247, 245, 241, 0.94);
    box-shadow: 0 3px 14px rgba(23, 48, 51, 0.08);
  }}

  div[data-testid="stExpander"] {{
    border: 1px solid var(--line);
    border-radius: {RADII['md']};
    background: rgba(247, 245, 241, 0.70);
    box-shadow: {SHADOWS['soft']};
  }}

  [data-testid="stDataFrame"] {{
    border: 1px solid var(--line);
    border-radius: {RADII['md']};
    overflow: hidden;
  }}

  .axis-letter {{
    display: inline-grid;
    place-items: center;
    width: 2.15rem;
    height: 2.15rem;
    margin-right: 0.42rem;
    border-radius: 50%;
    background: var(--deep-ink);
    color: var(--pearl-white);
    font-weight: 800;
    letter-spacing: 0;
  }}

  .axis-name {{
    display: block;
    min-height: 2.8rem;
    margin-bottom: 0.45rem;
    font-size: 1rem;
    line-height: 1.32;
  }}

  .evidence-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    margin: 0.18rem 0.18rem 0.18rem 0;
    padding: 0.3rem 0.55rem;
    border: 1px solid var(--line-strong);
    border-radius: {RADII['pill']};
    color: var(--deep-ink);
    font-size: 0.74rem;
    font-weight: 720;
  }}

  .state-positive {{ background: var(--mist-mint); border-left: 4px solid var(--deep-ink); }}
  .state-negative {{ background: var(--powder-aqua); border-left: 4px double var(--deep-ink); }}
  .state-null {{ background: var(--warm-ivory); border: 1px dashed var(--deep-ink); }}
  .state-not-tested {{ background: var(--pale-lavender); border: 1px dotted var(--deep-ink); }}
  .state-mixed {{ background: var(--soft-blush); border-left: 4px solid var(--champagne); }}

  .evidence-row {{
    padding: 0.72rem 0.8rem;
    margin: 0.42rem 0;
    border: 1px solid var(--line);
    border-radius: {RADII['sm']};
    background: rgba(247, 245, 241, 0.78);
  }}

  .evidence-row strong {{ color: var(--deep-ink); }}
  .evidence-meta {{ color: rgba(23, 48, 51, 0.72); font-size: 0.79rem; line-height: 1.45; }}

  .rank-kicker {{
    color: rgba(23, 48, 51, 0.72);
    font-size: 0.7rem;
    font-weight: 780;
    letter-spacing: 0.13em;
    text-transform: uppercase;
  }}

  .rank-one {{ border-top: 5px solid var(--champagne) !important; }}
  .rank-two {{ border-top: 5px solid var(--powder-aqua) !important; }}

  .st-key-product_hero {{
    position: relative;
    overflow: hidden;
    padding: 1.05rem 1.4rem 1.15rem;
    border: 1px solid var(--line);
    border-radius: {RADII['lg']};
    background: linear-gradient(112deg, rgba(247,245,241,0.96), rgba(221,235,229,0.70) 62%, rgba(220,233,236,0.72));
    box-shadow: {SHADOWS['soft']};
  }}

  .st-key-product_hero::after {{
    content: "";
    position: absolute;
    width: 12rem;
    height: 12rem;
    right: -3.2rem;
    top: -5.3rem;
    border: 1px solid rgba(217, 200, 174, 0.78);
    border-radius: 50%;
    box-shadow: inset 0 0 0 1.7rem rgba(232, 226, 238, 0.22);
  }}

  .st-key-product_hero h1 {{
    margin: 0.12rem 0 0.28rem !important;
    font-size: clamp(2.65rem, 4vw, 4rem) !important;
    line-height: 0.98 !important;
  }}

  .product-value {{
    max-width: 760px;
    font-size: clamp(1.18rem, 2.1vw, 1.65rem);
    font-weight: 630;
    line-height: 1.2;
    letter-spacing: -0.022em;
  }}

  .st-key-product_hero .skinexo-support {{
    margin-top: 0.38rem;
    font-size: 0.88rem;
    line-height: 1.35;
  }}

  .product-journey {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.55rem;
    margin: 0.55rem 0 0.35rem;
    color: rgba(23, 48, 51, 0.74);
  }}

  .journey-step {{
    padding: 0.25rem 0.58rem;
    border: 1px solid rgba(23, 48, 51, 0.13);
    border-radius: {RADII['pill']};
    background: rgba(247, 245, 241, 0.72);
    font-size: 0.7rem;
    font-weight: 760;
    letter-spacing: 0.09em;
    text-transform: uppercase;
  }}

  .journey-arrow {{ color: rgba(23, 48, 51, 0.36); font-size: 0.8rem; }}
  .anchor-target {{ scroll-margin-top: 4.2rem; }}

  .st-key-context_hero {{
    margin-top: 0.2rem;
    border-top: 4px solid var(--champagne) !important;
  }}

  .context-id {{
    margin-top: 0.12rem;
    font-size: 2rem;
    font-weight: 790;
    letter-spacing: -0.04em;
  }}

  .context-route {{
    margin-top: 0.05rem;
    font-size: 1.18rem;
    font-weight: 620;
  }}

  .context-condition {{
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.5rem 0.8rem;
    margin-top: 0.65rem;
    color: rgba(23, 48, 51, 0.76);
    font-size: 0.88rem;
  }}

  .context-condition span {{
    padding-left: 0.8rem;
    border-left: 1px solid var(--line-strong);
  }}

  .context-dataset {{
    font-size: 1.65rem;
    font-weight: 760;
    text-align: right;
  }}

  .status-pair {{ display: flex; justify-content: flex-end; gap: 0.42rem; margin-top: 0.45rem; }}
  .status-pair span {{
    padding: 0.28rem 0.58rem;
    border: 1px solid var(--line-strong);
    border-radius: {RADII['pill']};
    background: var(--mist-mint);
    font-size: 0.7rem;
    font-weight: 760;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }}

  .summary-copy {{
    margin: 0.45rem 0 0.75rem;
    font-size: 1.08rem;
    font-weight: 520;
    line-height: 1.58;
  }}

  .summary-retrieval {{
    display: flex;
    flex-direction: column;
    gap: 0.12rem;
    padding: 0.68rem 0.78rem;
    border-left: 4px solid var(--champagne);
    background: rgba(239, 234, 226, 0.62);
    border-radius: 0 {RADII['sm']} {RADII['sm']} 0;
  }}

  .summary-retrieval span {{ font-size: 0.7rem; font-weight: 740; letter-spacing: 0.07em; text-transform: uppercase; }}
  .summary-retrieval strong {{ font-size: 1.12rem; }}

  .signature-card {{
    height: 100%;
    padding: 1rem 1.05rem;
    border: 1px solid var(--line);
    border-radius: {RADII['md']};
    background: rgba(247, 245, 241, 0.80);
    box-shadow: {SHADOWS['soft']};
  }}

  .signature-row {{
    display: grid;
    grid-template-columns: 1.85rem minmax(10rem, 1fr) auto;
    align-items: center;
    gap: 0.48rem;
    min-height: 2.55rem;
    margin-top: 0.35rem;
    padding: 0.42rem 0.58rem;
    border: 1px solid var(--line);
    border-radius: {RADII['sm']};
    background: rgba(255,255,255,0.58);
  }}

  .signature-positive {{ border-left: 5px solid var(--deep-ink); background: rgba(221,235,229,0.58); }}
  .signature-negative {{ border-left: 5px double var(--deep-ink); background: rgba(220,233,236,0.58); }}
  .signature-null {{ border-style: dashed; background: rgba(239,234,226,0.62); }}
  .signature-not-tested, .signature-unknown {{ border-style: dotted; background: rgba(232,226,238,0.58); }}
  .signature-mixed {{ border-left: 5px solid var(--champagne); background: rgba(238,221,217,0.58); }}
  .signature-symbol {{ font-size: 1.28rem; font-weight: 800; text-align: center; }}
  .signature-name {{ display: flex; align-items: baseline; gap: 0.5rem; }}
  .signature-name small {{ color: rgba(23,48,51,0.62); font-weight: 760; }}
  .signature-state {{ font-size: 0.78rem; font-weight: 730; white-space: nowrap; }}
  .signature-row > small {{ display: none; }}
  .signature-legend {{ margin-top: 0.45rem; color: rgba(23,48,51,0.64); font-size: 0.68rem; }}

  .st-key-retrieval_hero {{
    margin-top: 0.7rem;
    border-top: 5px solid var(--champagne) !important;
    background: linear-gradient(118deg, rgba(247,245,241,0.92), rgba(220,233,236,0.55)) !important;
  }}

  .retrieval-context {{ font-size: 2.35rem; font-weight: 800; letter-spacing: -0.045em; }}
  .retrieval-route {{ margin-top: 0.15rem; font-size: 1.15rem; font-weight: 610; }}
  .retrieval-metric-label {{ font-size: 0.72rem; font-weight: 760; letter-spacing: 0.1em; text-transform: uppercase; }}
  .retrieval-value {{ margin: 0.08rem 0; font-size: clamp(3rem, 5vw, 4.5rem); font-weight: 820; line-height: 1; letter-spacing: -0.06em; }}

  .retrieval-evidence-card {{
    display: flex;
    flex-direction: column;
    min-height: 6.2rem;
    padding: 0.72rem 0.86rem;
    border: 1px solid var(--line);
    border-radius: {RADII['sm']};
    background: rgba(247,245,241,0.76);
  }}
  .retrieval-evidence-card strong {{ font-size: 1.62rem; line-height: 1.1; }}
  .retrieval-evidence-card span {{ margin-top: 0.24rem; font-size: 0.82rem; font-weight: 690; }}
  .retrieval-evidence-card small {{ margin-top: 0.18rem; color: rgba(23,48,51,0.62); font-size: 0.68rem; }}

  .why-lead {{ margin: 0.2rem 0 0.3rem; font-size: 1.12rem; line-height: 1.45; }}
  .program-chip {{
    margin: 0.28rem 0;
    padding: 0.38rem 0.52rem;
    border-left: 4px solid var(--deep-ink);
    border-radius: 0 {RADII['sm']} {RADII['sm']} 0;
    background: rgba(221,235,229,0.62);
    font-size: 0.78rem;
    font-weight: 610;
  }}
  .why-number {{ font-size: 2.8rem; font-weight: 810; letter-spacing: -0.05em; }}
  .difference-line {{ margin: 0.35rem 0; padding: 0.36rem 0.5rem; border: 1px solid var(--line); border-radius: {RADII['sm']}; font-size: 0.78rem; }}

  .snapshot-time {{ margin: 0.18rem 0 0.35rem; font-size: 2.25rem; font-weight: 800; letter-spacing: -0.04em; }}

  .reliability-grid {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 0.58rem;
  }}
  .reliability-item {{
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 0.18rem 0.7rem;
    padding: 0.68rem 0.75rem;
    border: 1px solid var(--line);
    border-radius: {RADII['sm']};
    background: rgba(247,245,241,0.74);
  }}
  .reliability-item span {{ font-size: 0.76rem; font-weight: 720; }}
  .reliability-item strong {{ font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; }}
  .reliability-item small {{ grid-column: 1 / -1; color: rgba(23,48,51,0.68); font-size: 0.67rem; line-height: 1.35; }}
  .reliability-verified {{ border-left: 5px solid var(--deep-ink); background: rgba(221,235,229,0.55); }}
  .reliability-limited {{ border-left: 5px solid var(--champagne); background: rgba(238,221,217,0.46); }}
  .reliability-unknown, .reliability-not-documented {{ border-style: dotted; background: rgba(232,226,238,0.52); }}

  .detail-list {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.3rem 1.2rem; }}
  .detail-row {{ display: grid; grid-template-columns: minmax(8rem, 0.42fr) 1fr; gap: 0.7rem; padding: 0.38rem 0; border-bottom: 1px solid rgba(23,48,51,0.10); }}
  .detail-row span {{ color: rgba(23,48,51,0.68); font-size: 0.76rem; }}
  .detail-row strong {{ font-size: 0.78rem; font-weight: 620; overflow-wrap: anywhere; }}

  [data-testid="stAlert"] {{
    border: 1px solid var(--line);
    border-radius: {RADII['md']};
    color: var(--deep-ink);
  }}

  hr {{ border-color: rgba(23, 48, 51, 0.10) !important; margin: 2.5rem 0 !important; }}

  a {{ color: var(--deep-ink) !important; text-decoration-color: var(--champagne) !important; }}
  code {{ font-family: {TYPOGRAPHY['mono']}; }}

  @media (max-width: 760px) {{
    .block-container {{ padding: 4rem 1rem 3rem; }}
    .skinexo-hero {{ padding: 1rem; }}
    h1 {{ font-size: 2.65rem !important; }}
    .product-journey {{ justify-content: flex-start; overflow-x: auto; }}
    .journey-arrow {{ display: none; }}
    .signature-row {{ grid-template-columns: 1.7rem 1fr; }}
    .signature-state {{ grid-column: 2; white-space: normal; }}
    .reliability-grid, .detail-list {{ grid-template-columns: 1fr; }}
    .context-dataset, .status-pair {{ text-align: left; justify-content: flex-start; }}
  }}

  @media (prefers-reduced-motion: reduce) {{
    *, *::before, *::after {{
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
      scroll-behavior: auto !important;
    }}
  }}
</style>
"""
