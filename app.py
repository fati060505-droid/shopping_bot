"""Product Helper: describe a product, its specs, or a problem, and get ranked buying advice."""
import streamlit as st

import config
from agents import advisor, intent as intent_agent, llm
from ranking.scorer import rank
from sources import active_source, fetch_products
from ui import components as ui
from ui.styles import inject

st.set_page_config(page_title="Product Helper", page_icon="🛍️", layout="centered", initial_sidebar_state="expanded")
inject()


@st.cache_data(ttl=config.CACHE_TTL_SECONDS, show_spinner=False)
def cached_search(query: str, source_key: str):
    """Cached so repeat searches never spend free API credits. source_key keeps caches separate per source."""
    products, source, warning = fetch_products(query)
    return [p.to_dict() for p in products], source, warning


# ---------- session state ----------
ss = st.session_state
ss.setdefault("messages", [])
ss.setdefault("searches", 0)

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("## What matters most?")
    st.caption("Set your priorities. They shape the ranking of every new search.")
    w_price = st.slider("Price", 0, 10, 5, help="Higher means cheaper products rank higher.")
    w_feat = st.slider("Features", 0, 10, 5, help="Higher means a closer match to your specs ranks higher.")
    w_rev = st.slider("Reviews", 0, 10, 5, help="Higher means well reviewed products rank higher.")
    if w_price + w_feat + w_rev == 0:
        w_price = w_feat = w_rev = 1
    budget_override = st.number_input(f"Max budget ({config.CURRENCY}, optional)", min_value=0, value=0, step=50)
    show_n = st.slider("Products to show", 3, 10, 5)
    st.divider()
    st.markdown(ui.source_badge(active_source()), unsafe_allow_html=True)
    st.markdown(
        f'<span class="badge {"live" if llm.available() else "demo"}">'
        f'{"AI advisor on" if llm.available() else "AI advisor off: add GROQ_API_KEY"}</span>',
        unsafe_allow_html=True,
    )
    st.caption(f"Searches this session: {ss.searches}/{config.MAX_SEARCHES_PER_SESSION}")
    if st.button("Clear conversation", use_container_width=True):
        ss.messages, ss.searches = [], 0
        st.rerun()

# ---------- header ----------
st.markdown(
    '<div class="hero"><h1>Find the right product, faster</h1>'
    "<p>Name a product, list the specs you need, or describe the problem you are trying to solve. "
    "I compare price, features and reviews, then tell you what I would buy.</p></div>",
    unsafe_allow_html=True,
)

# ---------- history ----------
for msg in ss.messages:
    with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"] == "user" else "🛍️"):
        if msg["role"] == "user":
            st.write(msg["text"])
        else:
            if msg.get("intent"):
                st.markdown(ui.intent_chips(msg["intent"]), unsafe_allow_html=True)
            if msg.get("verdict"):
                st.markdown('<div class="verdict"><div class="who">Advisor’s verdict</div></div>', unsafe_allow_html=True)
                st.markdown(msg["verdict"])
            for i, prod in enumerate(msg.get("products", []), 1):
                st.markdown(ui.product_card(prod, i), unsafe_allow_html=True)
            if msg.get("note"):
                st.caption(msg["note"])

if not ss.messages:
    st.markdown("**Try one of these:**")
    cols = st.columns(3)
    examples = [
        "Noise cancelling headphones under $150",
        "Laptop with 16GB RAM for programming, lightweight",
        "My phone battery dies before evening",
    ]
    for col, ex in zip(cols, examples):
        if col.button(ex, use_container_width=True):
            ss.pending = ex
            st.rerun()

user_text = st.chat_input("Describe a product, its specs, or your problem...") or ss.pop("pending", None)

# ---------- handle a new question ----------
if user_text:
    user_text = user_text.strip()[:500]
    ss.messages.append({"role": "user", "text": user_text})
    with st.chat_message("user", avatar="🧑‍💻"):
        st.write(user_text)

    with st.chat_message("assistant", avatar="🛍️"):
        if ss.searches >= config.MAX_SEARCHES_PER_SESSION:
            note = "You have reached this session's search limit, which protects the free API quota. Clear the conversation to start over."
            st.warning(note)
            ss.messages.append({"role": "assistant", "note": note})
        else:
            notes = []
            with st.status("Working on it...", expanded=True) as status:
                st.write("Understanding your request")
                history = [m["text"] for m in ss.messages if m["role"] == "user"][:-1]
                plan, warn = intent_agent.parse(user_text, history)
                if budget_override:
                    plan["budget"] = float(budget_override)
                notes += [warn] if warn else []

                st.write(f"Searching for: {plan['search_query']}")
                items, source, warn = cached_search(plan["search_query"], active_source())
                ss.searches += 1
                notes += [warn] if warn else []

                st.write("Ranking by your priorities")
                from sources.models import Product

                products = [Product(**{k: v for k, v in d.items() if k in Product.__dataclass_fields__}) for d in items]
                weights = {"price": w_price, "features": w_feat, "reviews": w_rev}
                ranked = rank(products, weights, plan["must_have"], plan["product_type"], plan.get("budget"))[:show_n]

                st.write("Asking the advisor")
                verdict, warn = advisor.advise(ranked, plan, weights, user_text)
                notes += [warn] if warn else []
                status.update(label="Done", state="complete", expanded=False)

            st.markdown(ui.intent_chips(plan), unsafe_allow_html=True)
            st.markdown('<div class="verdict"><div class="who">Advisor’s verdict</div></div>', unsafe_allow_html=True)
            st.markdown(verdict)
            payload = [p.to_dict() for p in ranked]
            for i, prod in enumerate(payload, 1):
                st.markdown(ui.product_card(prod, i), unsafe_allow_html=True)
            if source == "mock":
                notes.append("These results are demo data, not real listings. Add a SERPER_API_KEY to .env for live products.")
            note = " ".join(notes)
            if note:
                st.caption(note)
            ss.messages.append({"role": "assistant", "intent": plan, "verdict": verdict, "products": payload, "note": note})
