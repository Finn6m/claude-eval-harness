import re

def evaluate_rule(output: str, rule: str) -> dict:
    """
    Checks the model output against a rule string using regex pattern matching.
    Includes bullet_count, word_count, contains, not_contains, starts_with.
    Returns a dict with is_failure, confidence and a reason.
    """
    output_stripped = output.strip()

    # bullet_count == N - if no match then m = none and moves on to next check
    m = re.match(r"bullet_count\s*==\s*(\d+)", rule)
    if m:
        expected = int(m.group(1))
        bullets = len(re.findall(r"^\s*[-•*]\s+", output_stripped, re.MULTILINE)) #counts bullet points in the models output. findall returns a list of all matches. len() counts them.
        is_failure = bullets != expected
        return {
            "is_failure": is_failure,
            "confidence": 0.95, #hardcoded to 95% as there is either the right amount of bullet points or not.
            "reasoning": f"Expected {expected} bullets, found {bullets}",
        }

    # word_count < N, word_count <= N, word_count > N, word_count >= N
    m = re.match(r"word_count\s*([<>]=?)\s*(\d+)", rule)
    if m:
        op, n = m.group(1), int(m.group(2))
        wc = len(output_stripped.split())
        if op == "<":
            is_failure = wc >= n
        elif op == "<=":
            is_failure = wc > n
        elif op == ">":
            is_failure = wc <= n
        elif op == ">=":
            is_failure = wc < n
        else:
            is_failure = False
        return {
            "is_failure": is_failure,
            "confidence": 0.95,
            "reasoning": f"Word count is {wc}, rule: word_count {op} {n}",
        }

    # contains: "text"
    m = re.match(r'contains:\s*"(.+)"', rule)
    if m:
        needle = m.group(1)
        is_failure = not bool(re.search(rf'\b{re.escape(needle)}\b', output_stripped, re.IGNORECASE))
        return {
            "is_failure": is_failure,
            "confidence": 0.95,
            "reasoning": f"Output {'did not contain' if is_failure else 'contained'} required text: '{needle}'",
        }

    # not_contains: "text"
    m = re.match(r'not_contains:\s*"(.+)"', rule)
    if m:
        needle = m.group(1)
        is_failure = bool(re.search(rf'\b{re.escape(needle)}\b', output_stripped, re.IGNORECASE))
        return {
            "is_failure": is_failure,
            "confidence": 0.95,
            "reasoning": f"Output {'contained forbidden' if is_failure else 'correctly excluded'} text: '{needle}'",
        }

    # starts_with: "text"
    m = re.match(r'starts_with:\s*"(.+)"', rule)
    if m:
        prefix = m.group(1)
        is_failure = not output_stripped.lower().startswith(prefix.lower())
        return {
            "is_failure": is_failure,
            "confidence": 0.95,
            "reasoning": f"Output {'did not start' if is_failure else 'started'} with '{prefix}'",
        }

    return {
        "is_failure": False,
        "confidence": 0.1,
        "reasoning": f"Unknown rule format: '{rule}'",
    }

def evaluate_exact(output: str, expected: str) -> dict:
    """
    direct string comparison that takes the models output, compares it to the expected output in the test collection
    and if they match then it passes and if it doesnt match then it fails.
    """
    is_failure = output.strip().lower() != expected.strip().lower()
    return {
        "is_failure": is_failure,
        "confidence": 1.0,
        "reasoning": f"Output {'did not match' if is_failure else 'matched'} expected value",
    }