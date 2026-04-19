def validate(state):
    print("Validation Agent running...")

    if not state["old_name"] or not state["new_name"]:
        raise ValueError("Invalid input")

    return state