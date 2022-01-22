import json


def is_json(myjson):
    try:
        json_object = json.loads(myjson)
        return True
    except ValueError as e:
        return False


if __name__ == "__main__":
    is_json(string_)