"""Makes all `.sql` contents under `app.db.sql` available
as variables with names that match the filenames.
"""

import os
from types import SimpleNamespace


class Queries(SimpleNamespace):
    pass


queries = Queries()

stub_content = "from types import SimpleNamespace\nclass Queries(SimpleNamespace):\n"
dir_ = os.path.dirname(__file__)
for root, _, files in os.walk(dir_):
    for file in files:
        file_name, ext = os.path.splitext(file)
        if ext == ".sql":
            with open(os.path.join(root, file), "r") as f:
                if hasattr(queries, file_name):
                    raise Exception(f"Duplicate sql filename: {f}")
                setattr(queries, file_name, f.read())
                stub_content += f"    {file_name}: str\n"
stub_content += "queries: Queries"

with open(os.path.join(dir_, "__init__.pyi"), "w") as f:
    f.write(stub_content)

__all__ = ["queries"]
