from sqlalchemy.exc import IntegrityError


def integrity_error_message(exc: IntegrityError) -> str:
    message = str(exc.orig) if exc.orig else str(exc)
    if "academic_years_name_key" in message or "academic_years" in message and "name" in message:
        return "An academic year with this name already exists"
    if "grades_name_key" in message or ("grades" in message and "name" in message):
        return "A grade with this name already exists"
    if "subjects_code_key" in message:
        return "A subject with this code already exists"
    if "unique" in message.lower() or "duplicate" in message.lower():
        return "A record with the same unique value already exists"
    return "Database constraint violation"
