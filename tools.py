"""
The three FitFindr tools.

Each tool can be called and tested independently before being used by the
planning loop.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str
"""

import config
from generate import generate
from utils.data_loader import load_listings


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally
    a size and a price ceiling.

    Args:
        description:
            Keywords describing what the user wants,
            for example "vintage graphic tee".

        size:
            A size string to filter by, or None to skip size filtering.
            Matching is case-insensitive. Values such as "M" can match
            multi-size values such as "S/M".

        max_price:
            Maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dictionaries, best match first.

        Each listing contains:
            id, title, description, category, style_tags, size,
            condition, price, colors, brand, platform

        Returns an empty list when nothing matches.
    """
    listings = load_listings()

    stop_words = {
        "a",
        "an",
        "the",
        "for",
        "looking",
        "want",
        "need",
    }

    description_words = {
        word.lower().strip(".,!?-")
        for word in description.split()
        if word.strip()
        and word.lower().strip(".,!?-") not in stop_words
    }

    matches: list[tuple[int, dict]] = []

    for listing in listings:
        # Filter by maximum price.
        if max_price is not None and listing["price"] > max_price:
            continue

        # Filter by size.
        if size is not None:
            requested_size = size.lower().strip()
            listing_size = listing["size"].lower().strip()

            # Split values such as "S/M", "M/L", or "XL (oversized)"
            # into individual parts so we avoid unsafe substring matching.
            size_parts = (
                listing_size
                .replace("(", " ")
                .replace(")", " ")
                .replace("/", " ")
                .replace("-", " ")
                .split()
            )

            if (
                requested_size != listing_size
                and requested_size not in size_parts
            ):
                continue

        searchable_text = " ".join(
            [
                listing["title"],
                listing["description"],
                listing["category"],
                " ".join(listing["style_tags"]),
                " ".join(listing["colors"]),
                listing["brand"] or "",
            ]
        ).lower()

        score = 0

        for word in description_words:
            if word in searchable_text:
                score += 1

        # Ignore listings with no keyword overlap.
        if score > 0:
            matches.append((score, listing))

    # Highest keyword score first.
    matches.sort(key=lambda item: item[0], reverse=True)

    return [
        listing
        for _, listing in matches[: config.SEARCH_RESULT_LIMIT]
    ]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    Args:
        new_item:
            A listing dictionary for the item the user is considering.

        wardrobe:
            A wardrobe dictionary with an "items" key containing a list
            of wardrobe item dictionaries.

    Returns:
        A non-empty string containing outfit suggestions.

        If the wardrobe is empty, returns general styling advice for the
        new item instead of failing.
    """
    wardrobe_items = wardrobe.get("items", [])

    item_details = (
        f"{new_item['title']} "
        f"({new_item['category']}, "
        f"colors: {', '.join(new_item['colors'])}, "
        f"style: {', '.join(new_item['style_tags'])})"
    )

    if not wardrobe_items:
        prompt = f"""
You are helping someone style a thrifted clothing item.

New item:
{item_details}

The user's wardrobe is empty.

Suggest one or two general outfit ideas for this item.
Keep the advice simple, practical, and specific.
"""

        return generate(prompt).strip()

    wardrobe_text = "\n".join(
        f"- {item['name']} | "
        f"category: {item['category']} | "
        f"colors: {', '.join(item['colors'])} | "
        f"style: {', '.join(item['style_tags'])} | "
        f"notes: {item.get('notes', '')}"
        for item in wardrobe_items
    )

    prompt = f"""
You are helping someone style a thrifted clothing item.

New item:
{item_details}

The user already owns these wardrobe pieces:
{wardrobe_text}

Suggest one or two outfits using the new item and pieces from the user's
wardrobe.

Name the wardrobe pieces you recommend.
Keep the answer short, practical, and easy to understand.
"""

    return generate(prompt).strip()


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would realistically post about the thrift find.

    Args:
        outfit:
            The outfit suggestion returned by suggest_outfit().

        new_item:
            The listing dictionary for the selected item.

    Returns:
        A two-to-four sentence fit-card caption.

        If outfit is empty or contains only whitespace, returns a descriptive
        message instead of raising an exception.
    """
    if not outfit or not outfit.strip():
        return (
            "I couldn't create a fit card because no outfit suggestion "
            "was provided."
        )

    prompt = f"""
Write a short social-media-style fit card for this thrift find.

Item:
- Title: {new_item['title']}
- Category: {new_item['category']}
- Price: ${new_item['price']:.2f}
- Platform: {new_item['platform']}
- Colors: {', '.join(new_item['colors'])}
- Style: {', '.join(new_item['style_tags'])}

Outfit suggestion:
{outfit}

Requirements:
- Write 2 to 4 sentences.
- Mention the item's title or category.
- Mention the price once.
- Mention the platform once.
- Include at least one piece or styling idea from the outfit suggestion.
- Make it sound like something a real person would post.
- Mention the overall vibe.
- Do not sound like a product listing.
"""

    return generate(prompt).strip()