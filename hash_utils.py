import hashlib

def hash_password(password_raw):
    password_bytes = password_raw.encode("utf-8")
    hasher = hashlib.sha256()
    hasher.update(password_bytes)
    password_hash = hasher.hexdigest()

    return password_hash

