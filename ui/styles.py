"""Theme: deep navy surfaces, violet for actions, teal for the winner, amber for stars."""
import streamlit as st

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@500;600;700&family=DM+Sans:wght@400;500;600&display=swap');
:root{--bg:#0F1224;--surface:#1A1F3A;--surface2:#232950;--line:#2E3566;--violet:#7C6CF0;--teal:#2DD4BF;--amber:#F5B83D;--text:#E8EAF6;--muted:#9AA0C8;--rose:#F472B6}
html,body,[class*="css"],.stApp{font-family:'DM Sans',sans-serif}
.stApp{background:radial-gradient(1200px 500px at 85% -10%,rgba(124,108,240,.18),transparent 60%),var(--bg)}
#MainMenu,footer{visibility:hidden}
.block-container{padding-top:2rem;max-width:980px}
h1,h2,h3{font-family:'Sora',sans-serif!important;letter-spacing:-.01em}

.hero{padding:1.2rem 0 .4rem}
.hero h1{font-size:2.3rem;line-height:1.15;margin:0;color:var(--text)}
.hero p{color:var(--muted);margin:.5rem 0 0;font-size:1.02rem;max-width:620px}

section[data-testid="stSidebar"]{background:var(--surface);border-right:1px solid var(--line)}
section[data-testid="stSidebar"] h2,section[data-testid="stSidebar"] h3{font-size:1.05rem}

.badge{display:inline-block;padding:.18rem .6rem;border-radius:999px;font-size:.78rem;font-weight:500;border:1px solid var(--line);color:var(--muted);background:var(--surface)}
.badge.live{color:var(--teal);border-color:rgba(45,212,191,.45);background:rgba(45,212,191,.08)}
.badge.demo{color:var(--amber);border-color:rgba(245,184,61,.45);background:rgba(245,184,61,.08)}

.intent{display:flex;flex-wrap:wrap;gap:.4rem;margin:.2rem 0 .9rem}
.chip{padding:.2rem .65rem;border-radius:8px;background:var(--surface2);color:var(--text);font-size:.84rem;border:1px solid var(--line)}

.verdict{background:linear-gradient(135deg,rgba(124,108,240,.16),rgba(45,212,191,.08));border:1px solid rgba(124,108,240,.5);border-radius:16px;padding:1rem 1.2rem;margin:.4rem 0 1.1rem}
.verdict .who{font-family:'Sora',sans-serif;font-weight:600;color:var(--violet);margin-bottom:.35rem;font-size:.95rem}

.card{display:flex;gap:1rem;background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:1rem;margin:0 0 .8rem;position:relative}
.card.top{border-color:var(--teal);box-shadow:0 0 0 1px rgba(45,212,191,.35)}
.rank{flex:0 0 2.1rem;height:2.1rem;border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Sora',sans-serif;font-weight:700;background:var(--surface2);color:var(--text)}
.card.top .rank{background:var(--teal);color:#06231F}
.thumb{flex:0 0 84px;height:84px;border-radius:12px;background:var(--surface2) center/contain no-repeat;border:1px solid var(--line)}
.body{flex:1;min-width:0}
.ttl{font-weight:600;color:var(--text);line-height:1.3;margin-bottom:.2rem}
.meta{color:var(--muted);font-size:.86rem}
.price{font-family:'Sora',sans-serif;font-weight:600;font-size:1.25rem;color:var(--text)}
.stars{color:var(--amber);letter-spacing:.05em}
.ribbon{position:absolute;top:-.6rem;right:1rem;background:var(--teal);color:#06231F;font-weight:600;font-size:.78rem;padding:.15rem .7rem;border-radius:999px}
.bars{display:grid;grid-template-columns:repeat(3,1fr);gap:.8rem;margin:.6rem 0 .7rem}
.bar .lab{display:flex;justify-content:space-between;font-size:.76rem;color:var(--muted);margin-bottom:.2rem}
.bar .track{height:6px;background:var(--surface2);border-radius:99px;overflow:hidden}
.bar .fill{height:100%;border-radius:99px}
.f-price{background:var(--violet)}.f-features{background:var(--teal)}.f-reviews{background:var(--amber)}
.cta{display:inline-block;padding:.42rem 1rem;border-radius:10px;background:var(--violet);color:#fff!important;font-weight:600;font-size:.88rem;text-decoration:none!important}
.cta:hover{background:#907fff}
.score{float:right;color:var(--muted);font-size:.82rem}
@media (max-width:640px){.card{flex-wrap:wrap}.thumb{display:none}.bars{grid-template-columns:1fr}}
</style>
"""


def inject() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
