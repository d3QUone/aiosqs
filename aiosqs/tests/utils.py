import os


def load_fixture(filename: str):
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(tests_dir, "fixtures", filename)
    with open(path, "r") as f:
        return f.read()
