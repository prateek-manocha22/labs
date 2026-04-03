# def json_to_toon(data: list[dict]) -> str:
#     """
#     Convert a list of uniform dicts to TOON format.

#     Example:
#         Input:  [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
#         Output:
#             # fields: id, name
#             1 | Alice
#             2 | Bob

#     Returns:
#         A single TOON-format string.
#     """
#     # TODO: Extract the field names from the first dict
#     # TODO: Build the header line: "# fields: key1, key2, ..."
#     # TODO: Build each data row: "val1 | val2 | ..."
#     # TODO: Join and return all lines as a string
#     pass


# def count_tokens(text: str) -> int:
#     """
#     A simple proxy for token count: split on whitespace and count words.
    
#     Args:
#         text: Any string.

#     Returns:
#         Integer word count.
#     """
#     # TODO: Implement this
#     pass

# ____________________________________________________________________________________________________

def json_to_toon(data: list[dict]) -> str:
    """
    Convert a list of uniform dicts to TOON format.

    Example:
        Input:  [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
        Output:
            # fields: id, name
            1 | Alice
            2 | Bob

    Returns:
        A single TOON-format string.
    """
    # TODO: Extract the field names from the first dict
    fields = list(data[0].keys())

    # TODO: Build the header line: "# fields: key1, key2, ..."
    header = "# fields: " + ", ".join(fields)

    # TODO: Build each data row: "val1 | val2 | ..."
    rows = [" | ".join(str(record[f]) for f in fields) for record in data]

    # TODO: Join and return all lines as a string
    return "\n".join([header] + rows)

    pass



def count_tokens(text: str) -> int:
    """
    A simple proxy for token count: split on whitespace and count words.
    
    Args:
        text: Any string.

    Returns:
        Integer word count.
    """
    # TODO: Implement this
    if not text:
        return 0
    return len(text.split())
    pass