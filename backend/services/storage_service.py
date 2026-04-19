import os

def save_file(file, filename):
    os.makedirs("storage", exist_ok=True)

    path = f"storage/{filename}"

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path