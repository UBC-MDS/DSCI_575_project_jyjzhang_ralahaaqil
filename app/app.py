"""Streamlit UI for product review search."""

from __future__ import annotations

import sys
from pathlib import Path

import duckdb
import streamlit as st
from langchain_core.documents import Document

from src.bm25 import search

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent
REVIEWS_PARQUET = PROJECT_ROOT / "data" / "raw" / "reviews.parquet"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FAISS_INDEX_DIR = PROJECT_ROOT / "outputs" / "faiss_index"


def _semantic_search(query: str, *, index_path: str, top_k: int):
    """Load embedding/FAISS stack only when semantic search runs."""
    from src.semantic import faiss_search

    return faiss_search(query, index_path=index_path, top_k=top_k)


def _hybrid_search(query: str):
    """Load hybrid stack only when hybrid search runs."""
    from src.hybrid_retrieval import hybrid_retrieval

    return hybrid_retrieval(query)


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


def _init_semantic_session() -> None:
    if "semantic_results" not in st.session_state:
        st.session_state.semantic_results = None
    if "semantic_error" not in st.session_state:
        st.session_state.semantic_error = None


def _init_hybrid_session() -> None:
    if "hybrid_results" not in st.session_state:
        st.session_state.hybrid_results = None
    if "hybrid_error" not in st.session_state:
        st.session_state.hybrid_error = None


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


def _render_hit(
    rank: int,
    score: float | None,
    doc: Document,
    *,
    metric_label: str = "Retrieval score",
    show_score: bool = True,
) -> None:
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
        columns = st.columns(2) if show_score else st.columns(1)
        with columns[0]:
            if rating is not None:
                stars = _rating_stars(rating)
                st.markdown(f"Rating: {stars} **{rating:.1f}** / 5")
            else:
                st.markdown("Rating: **N/A**")
        if show_score:
            with columns[1]:
                if score is None:
                    st.metric(metric_label, "N/A")
                else:
                    st.metric(metric_label, f"{score:.4f}")


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
    _init_semantic_session()
    _init_hybrid_session()

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
                    st.session_state.bm25_results = search(query.strip(), top_k=3)
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
            for i, (doc, score) in enumerate(st.session_state.bm25_results, start=1):
                _render_hit(i, score, doc)
        else:
            st.info(
                "Enter a query and press **Search** or **Enter** to run BM25 retrieval."
            )

    elif search_mode == "Semantic":
        st.caption(
            "Dense retrieval over the FAISS index (L2 distance; lower is better). "
            f'Last query: "{query.strip() or "—"}"'
        )

        if submitted and query.strip():
            with st.spinner("Searching FAISS index…"):
                try:
                    st.session_state.semantic_results = _semantic_search(
                        query.strip(),
                        index_path=str(FAISS_INDEX_DIR),
                        top_k=3,
                    )
                    st.session_state.semantic_error = None
                except FileNotFoundError as exc:
                    st.session_state.semantic_error = str(exc)
                    st.session_state.semantic_results = None
                except Exception as exc:  # pragma: no cover - defensive UI
                    st.session_state.semantic_error = f"{type(exc).__name__}: {exc}"
                    st.session_state.semantic_results = None

        if st.session_state.semantic_error:
            st.error(st.session_state.semantic_error)
        elif st.session_state.semantic_results:
            for i, (doc, score) in enumerate(
                st.session_state.semantic_results, start=1
            ):
                _render_hit(i, score, doc, metric_label="L2 distance")
        else:
            st.info(
                "Enter a query and press **Search** or **Enter** to run semantic retrieval."
            )

    elif search_mode == "Hybrid":
        st.caption(
            "Hybrid retrieval via EnsembleRetriever (BM25 + FAISS). "
            f'Last query: "{query.strip() or "—"}"'
        )

        if submitted and query.strip():
            with st.spinner("Running hybrid retrieval…"):
                try:
                    docs = _hybrid_search(query.strip())
                    st.session_state.hybrid_results = list(docs)[:3]
                    st.session_state.hybrid_error = None
                except FileNotFoundError as exc:
                    st.session_state.hybrid_error = str(exc)
                    st.session_state.hybrid_results = None
                except Exception as exc:  # pragma: no cover - defensive UI
                    st.session_state.hybrid_error = f"{type(exc).__name__}: {exc}"
                    st.session_state.hybrid_results = None

        if st.session_state.hybrid_error:
            st.error(st.session_state.hybrid_error)
        elif st.session_state.hybrid_results:
            for i, doc in enumerate(st.session_state.hybrid_results, start=1):
                _render_hit(i, None, doc, show_score=False)
        else:
            st.info(
                "Enter a query and press **Search** or **Enter** to run hybrid retrieval."
            )

    st.caption(f"Mode selected: **{search_mode}**.")


if __name__ == "__main__":
    main()
