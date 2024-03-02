def validate_affordability(
    mortgage: int,
    salary: int,
    affordability: float,
    existing_customer: bool,
) -> bool:
    """Check whether a proposed mortgage is afforadble.

    Args:
        mortgage: total size of the mortagage to be taken out
        salary: total salary of the individual
        affordability: expected minimum ratio of mortagage to salary.
        existing_customer: are they an existing customer?

    Returns:
        bool: True for a successful affordability test or False for failure.
    """
    if not salary:
        return False

    if existing_customer or mortgage < 20000 or (mortgage / salary) <= affordability:
        return True

    return False
