DIFF_CHAR_LIMIT = 8000

def get_diff(state) -> str:
    return state["raw_diff"][:DIFF_CHAR_LIMIT]