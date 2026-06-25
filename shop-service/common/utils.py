def format_date_fields(record: dict, fields: tuple) -> dict:
    for field in fields:
        if record.get(field):
            record[field] = record[field].isoformat()
    return record


def format_date_fields_list(records: list, fields: tuple) -> list:
    for record in records:
        format_date_fields(record, fields)
    return records