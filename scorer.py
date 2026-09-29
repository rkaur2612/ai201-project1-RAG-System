def judge(question, expects, answer, results) -> bool:
    """
    q: 'give', expect: 'give'
    the expect is in the answer
    """
    return expects.lower().strip() in answer.lower()