# def retrieve(chunks: list[str], question: str) -> str:
#     """
#     Retrieve the most relevant chunk using simple word overlap.

#     Args:
#         chunks:   List of text strings (the knowledge base).
#         question: The user's question.

#     Returns:
#         The single chunk string with the highest word overlap score.
#     """
#     # TODO: Tokenize question (split on spaces, lowercase)
#     # TODO: For each chunk, count how many question words appear in it
#     # TODO: Return the chunk with the highest count
#     pass


# def answer(chunks: list[str], question: str) -> dict:
#     """
#     Retrieve the best context and build a simple answer.

#     Args:
#         chunks:   The knowledge base.
#         question: The user's question.

#     Returns:
#         A dict with keys: 'context' (str) and 'answer' (str).
#         'answer' must be a non-empty string.
#     """
#     # TODO: Call retrieve() to get the best chunk
#     # TODO: Return {"context": <chunk>, "answer": <any non-empty string>}
#     pass

#_________________________________________________________________________________________

def retrieve(chunks: list[str], question: str) -> str:
    """
    Retrieve the most relevant chunk using simple word overlap.

    Args:
        chunks:   List of text strings (the knowledge base).
        question: The user's question.

    Returns:
        The single chunk string with the highest word overlap score.
    """
    # TODO: Tokenize question (split on spaces, lowercase)
    question_words = set(question.lower().split())
    # TODO: For each chunk, count how many question words appear in it
    def overlap_score(chunk):
        chunk_words = set(chunk.lower().split())
        return len(question_words & chunk_words)
    # TODO: Return the chunk with the highest count
    return max(chunks, key=overlap_score)
    


def answer(chunks: list[str], question: str) -> dict:
    """
    Retrieve the best context and build a simple answer.

    Args:
        chunks:   The knowledge base.
        question: The user's question.

    Returns:
        A dict with keys: 'context' (str) and 'answer' (str).
        'answer' must be a non-empty string.
    """
    # TODO: Call retrieve() to get the best chunk
    context = retrieve(chunks, question)
    # TODO: Return {"context": <chunk>, "answer": <any non-empty string>}
    return {"context": context, "answer": context}