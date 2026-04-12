"""Streamlit UI for product review search."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
from langchain_core.documents import Document

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.bm25 import search_all_shards 

MOCK_RESULTS = [
    {
        "title": "Wireless Bluetooth Headphones Pro",
        "review": (
            "These sound excellent for the price. Battery life is solid and the noise "
            "cancellation works well on flights. The ear cups are comfortable for long "
            "sessions though they can get a bit warm in summer. Pairing was instant on "
            "my phone. I would buy again."
        ),
        "rating": 4.5,
        "score": 18.42,
    },
    {
        "title": "Stainless Steel French Press",
        "review": (
            "Makes great coffee and feels sturdy. The mesh filter is finer than my old "
            "press so fewer grounds slip through. Cleanup is easy if you rinse right "
            "away. A little heavy but that is expected for steel."
        ),
        "rating": 4.0,
        "score": 14.07,
    },
    {
        "title": "USB-C Hub with HDMI",
        "review": (
            "All ports work as advertised. HDMI is stable at 4K. Gets warm under load "
            "but not hot. Cable could be longer for my desk setup."
        ),
        "rating": 3.5,
        "score": 9.88,
    },
]


def _truncate(text: str, max_chars: int = 200) -> str:
    text = text.strip()
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def _rating_stars(rating: float) -> str:
    n = max(0, min(5, round(rating)))
    filled, empty = "\u2605", "\u2606"
    return filled * n + empty * (5 - n)


def _init_bm25_session() -> None:
    if "bm25_results" not in st.session_state:
        st.session_state.bm25_results = None
    if "bm25_error" not in st.session_state:
        st.session_state.bm25_error = None


def _metadata_rating(metadata: dict) -> float | None:
    raw = metadata.get("average_rating")
    if raw is None:
        return None
    try:
        r = float(raw)
    except (TypeError, ValueError):
        return None
    if r < 0:
        return None
    return r


def _review_display_text(doc: Document) -> str:
    md = doc.metadata
    review = md.get("review_text")
    if review is not None and str(review).strip():
        return str(review).strip()
    return doc.page_content


def _render_hit(rank: int, score: float, doc: Document) -> None:
    md = doc.metadata
    product = md.get("product")
    asin = md.get("parent_asin")
    product_str = str(product).strip() if product is not None else ""
    if product_str:
        title_line = product_str
    else:
        title_line = f"Unknown product (ASIN: `{asin or '—'}`)"
    rating = _metadata_rating(md)

    with st.container(border=True):
        st.markdown(f"**{rank}. {title_line}**")
        if product_str and asin:
            st.caption(f"ASIN: `{asin}`")
        st.caption(_truncate(_review_display_text(doc)))
        col_rating, col_score = st.columns(2)
        with col_rating:
            if rating is not None:
                stars = _rating_stars(rating)
                st.markdown(f"Rating: {stars} **{rating:.1f}** / 5")
            else:
                st.markdown("Rating: **N/A**")
        with col_score:
            st.metric("Retrieval score", f"{score:.4f}")


def _hide_streamlit_chrome() -> None:
    st.markdown(
        """
        <style>
        #MainMenu {visibility: hidden;}
        .stDeployButton, .stAppDeployButton {display: none !important;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Review search", layout="centered")
    _hide_streamlit_chrome()
    st.title("Product review search")
    _init_bm25_session()

    st.caption("Search mode")
    search_mode = st.radio(
        "Search mode",
        options=["BM25", "Semantic", "Hybrid"],
        horizontal=True,
        label_visibility="collapsed",
    )

    with st.form("query_form", clear_on_submit=False):
        query = st.text_input(
            "Query",
            placeholder="e.g. comfortable headphones for travel",
            label_visibility="collapsed",
        )
        submitted = st.form_submit_button("Search")

    st.divider()
    st.subheader("Top results")

    if search_mode == "BM25":
        st.caption(
            "BM25 over sharded index. "
            f'Last query: "{query.strip() or "—"}"'
        )

        if submitted and query.strip():
            with st.spinner("Searching BM25 shards (this may take a while)…"):
                try:
                    st.session_state.bm25_results = search_all_shards(
                        query.strip(), top_k=3
                    )
                    st.session_state.bm25_error = None
                except FileNotFoundError as exc:
                    st.session_state.bm25_error = str(exc)
                    st.session_state.bm25_results = None
                except Exception as exc:  # pragma: no cover - defensive UI
                    st.session_state.bm25_error = f"{type(exc).__name__}: {exc}"
                    st.session_state.bm25_results = None

        if st.session_state.bm25_error:
            st.error(st.session_state.bm25_error)
        elif st.session_state.bm25_results:
            for i, (score, doc) in enumerate(st.session_state.bm25_results, start=1):
                _render_hit(i, score, doc)
        else:
            st.info("Enter a query and press **Search** or **Enter** to run BM25 retrieval.")

    else:
        st.caption(
            "Placeholder data for Semantic / Hybrid (not wired yet). "
            f'Query: "{query.strip() or "—"}"'
        )
        for i, item in enumerate(MOCK_RESULTS, start=1):
            with st.container(border=True):
                st.markdown(f"**{i}. {item['title']}**")
                st.caption(_truncate(item["review"]))
                col_rating, col_score = st.columns(2)
                with col_rating:
                    stars = _rating_stars(item["rating"])
                    st.markdown(f"Rating: {stars} **{item['rating']:.1f}** / 5")
                with col_score:
                    st.metric("Retrieval score", f"{item['score']:.2f}")

    st.caption(f"Mode selected: **{search_mode}**.")


if __name__ == "__main__":
    main()
