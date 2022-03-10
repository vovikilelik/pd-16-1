import json


def load_json(file_name):
    with open(file_name) as f:
        return json.load(f)


def json_reader(file_name, row_reader):
    json_data = load_json(file_name)

    for row in json_data:
        row_reader(row)


def create_serialize_mapper(*fields):
    def mapper(row):
        raw_dict = row.__dict__
        serialized_row = {}
        for key in fields:
            serialized_row[key] = raw_dict.get(key)

        return serialized_row

    return mapper


def serialize(rows, mapper):
    data = []
    for row in rows:
        data.append(mapper(row))

    return data


def print_pre(text):
    return f'<pre>{text}</pre>'
