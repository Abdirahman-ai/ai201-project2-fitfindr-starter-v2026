"""
The FitFindr planning loop.

This file makes FitFindr an agent rather than a fixed sequence of tool calls.
It decides what to do next based on what the previous step returned.

    python agent.py
"""

import re

import trace
from tools import search_listings, suggest_outfit, create_fit_card

# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    Create a fresh session for one user interaction.

    Every tool result is stored in the session, and later tools read their
    inputs back from that session so the state is visible and testable.
    """
    return {
        "query": query,
        "parsed": {},
        "search_results": [],
        "selected_item": None,
        "wardrobe": wardrobe,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None,
    }


# ── query parsing ─────────────────────────────────────────────────────────────

def _parse_query(query: str) -> dict:
    """
    Extract description, optional size, and optional maximum price
    using regular expressions and simple string cleanup.
    """
    price_match = re.search(
        r"under\s*\$?(\d+(?:\.\d+)?)",
        query,
        re.IGNORECASE,
    )

    max_price = (
        float(price_match.group(1))
        if price_match
        else None
    )

    size_match = re.search(
        r"\bsize\s+([A-Za-z0-9./-]+)",
        query,
        re.IGNORECASE,
    )

    size = size_match.group(1) if size_match else None

    description = query

    # Remove the price phrase from the description.
    if price_match:
        description = (
            description[:price_match.start()]
            + description[price_match.end():]
        )

    # Find the size phrase again after the price phrase has been removed.
    size_match_after_price = re.search(
        r"\bsize\s+([A-Za-z0-9./-]+)",
        description,
        re.IGNORECASE,
    )

    if size_match_after_price:
        description = (
            description[:size_match_after_price.start()]
            + description[size_match_after_price.end():]
        )

    description = description.strip(" ,.-")

    return {
        "description": description,
        "size": size,
        "max_price": max_price,
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the FitFindr planning loop once and return the finished session.

    The loop moves through these steps:

        parse
          ↓
        search
          ├── no matches → stop with a useful error
          ↓
        suggest_outfit
          ↓
        create_fit_card
          ↓
        done
    """
    session = new_session(query, wardrobe)

    step = "parse"
    iteration_count = 0

    while step != "done":
        iteration_count += 1
        trace.check_iterations(iteration_count)

        if step == "parse":
            session["parsed"] = _parse_query(session["query"])
            step = "search"

        elif step == "search":
            session["search_results"] = search_listings(
                description=session["parsed"]["description"],
                size=session["parsed"]["size"],
                max_price=session["parsed"]["max_price"],
            )

            # Branch: stop if search returned nothing.
            if not session["search_results"]:
                session["error"] = (
                    "I couldn't find a matching listing. "
                    "Try increasing your budget, using a different size, "
                    "or using a broader item description."
                )
                step = "done"
                continue

            # Choose the best-ranked result and store it in session state.
            session["selected_item"] = session["search_results"][0]
            step = "suggest_outfit"

        elif step == "suggest_outfit":
            session["outfit_suggestion"] = suggest_outfit(
                session["selected_item"],
                session["wardrobe"],
            )
            step = "create_fit_card"

        elif step == "create_fit_card":
            session["fit_card"] = create_fit_card(
                session["outfit_suggestion"],
                session["selected_item"],
            )
            step = "done"

    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(
            f"  fit_card is {session['fit_card']!r} "
            "— it should still be None here"
        )
        return

    item = session["selected_item"] or {}

    print(
        f"  found:    {item.get('title')} — "
        f"${item.get('price')} on {item.get('platform')}"
    )
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(
        run_agent(
            query="looking for a vintage graphic tee under $30",
            wardrobe=get_example_wardrobe(),
        )
    )

    print("\n=== A query it can't ===")
    _show(
        run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_example_wardrobe(),
        )
    )

    print(
        "\nThe second one should stop before the fit card. "
        "If both paths look the same,\n"
        "the branch isn't doing anything."
    )