def summarize_text(text: str) -> dict:
    """
    Simulate an LLM-style structured JSON summarization.

    Args:
        text: Any plain text string.

    Returns:
        A dict with keys: 'title' (str), 'points' (list of 3 str), 'sentiment' (str)
        
    Example output:
        {
            "title": "AI improves traffic flow",
            "points": ["Reduces wait times", "Uses computer vision", "Deployed in 5 cities"],
            "sentiment": "positive"
        }
    """
    words = text.split()
    # Build a deterministic title from the first 6 words of the input
    title = " ".join(words[:6]) if len(words) >= 6 else " ".join(words)

    # Split the text into three roughly equal parts for three bullet points
    chunk_size = max(1, len(words) // 3)
    points = [
        " ".join(words[:chunk_size]),
        " ".join(words[chunk_size: chunk_size * 2]),
        " ".join(words[chunk_size * 2:]) or "Additional insights available",
    ]

    # Simple keyword-based sentiment
    positive_words = {"good", "great", "improving", "optimizing", "transforming", "better", "best", "efficient"}
    negative_words = {"bad", "poor", "failing", "broken", "worst", "slow", "error"}
    lower_text = text.lower()
    pos_count = sum(1 for w in positive_words if w in lower_text)
    neg_count = sum(1 for w in negative_words if w in lower_text)

    if pos_count > neg_count:
        sentiment = "positive"
    elif neg_count > pos_count:
        sentiment = "negative"
    else:
        sentiment = "neutral"

    return {
        "title": title,
        "points": points,
        "sentiment": sentiment,
    }
