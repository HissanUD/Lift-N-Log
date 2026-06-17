def get_id(db):
    if len(db) == 0:
        return 1
    highest_id = 0
    for exercise in db:
        if exercise["id"]> highest_id:
            highest_id = exercise["id"]
    return highest_id + 1