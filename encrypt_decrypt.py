def do_magic(msg, key):
    length = len(msg)
    output_str = ""
    while len(key) < length:
        key += key
    for i in range(length):
        current = msg[i]
        current_key = key[i % len(key)]
        output_str += chr(ord(current) ^ ord(current_key))
    return str(output_str)


if __name__ == "__main__":
    do_magic(msg, key)