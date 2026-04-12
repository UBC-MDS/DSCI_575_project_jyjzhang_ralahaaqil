"""Streamlit UI for product review search."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import streamlit as st
from langchain_core.documents import Document

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
REVIEWS_PARQUET = PROJECT_ROOT / "data" / "raw" / "reviews.parquet"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.bm25 import search

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


@st.cache_data(show_spinner=False)
def _first_raw_review_text(parent_asin: str) -> str | None:
    """First matching row in raw reviews for this ASIN (ordered by title, text)."""
    if not REVIEWS_PARQUET.is_file():
        return None
    try:
        with duckdb.connect() as con:
            row = con.execute(
                """
                SELECT title, text
                FROM read_parquet(?)
                WHERE parent_asin = ?
                ORDER BY title NULLS FIRST, text NULLS FIRST
                LIMIT 1
                """,
                [str(REVIEWS_PARQUET.resolve()), parent_asin],
            ).fetchone()
    except Exception:
        return None
    if not row:
        return None
    title, text = row[0], row[1]
    parts: list[str] = []
    if title is not None and str(title).strip():
        parts.append(str(title).strip())
    if text is not None and str(text).strip():
        parts.append(str(text).strip())
    return " ".join(parts) if parts else None


def _review_snippet_for_hit(doc: Document, parent_asin: str | None) -> str:
    if parent_asin:
        raw = _first_raw_review_text(parent_asin)
        if raw:
            return raw
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
    asin_lookup = (str(asin).strip() if asin is not None else "") or None

    with st.container(border=True):
        st.markdown(f"**{rank}. {title_line}**")
        if product_str and asin:
            st.caption(f"ASIN: `{asin}`")
        st.caption(_truncate(_review_snippet_for_hit(doc, asin_lookup)))
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
            "BM25 over the full preprocessed index. "
            f'Last query: "{query.strip() or "—"}"'
        )

        if submitted and query.strip():
            with st.spinner("Searching BM25 index…"):
                try:
                    st.session_state.bm25_results = search(
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
