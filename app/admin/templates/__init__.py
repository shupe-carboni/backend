"""Setup a stub file revealing available files in the namespace and return them through
a dynamic file read, which assumes the attribute name matches the file name"""

import os
from io import BytesIO
from types import SimpleNamespace
from logging import getLogger

logger = getLogger("uvicorn.info")


class Templates(SimpleNamespace):
    dir_ = os.path.dirname(__file__)

    def __getattr__(self, filename):
        with open(os.path.join(self.dir_, f"{filename}.xlsx"), "rb") as f:
            file_data = BytesIO(f.read())
            file_data.seek(0)
            return file_data


stub_content = "from io import BytesIO\n"
stub_content += (
    "from types import SimpleNamespace\n\nclass Templates(SimpleNamespace):\n"
)

dir_ = os.path.dirname(__file__)
for root, _, files in os.walk(dir_):
    for file in files:
        file_name, ext = os.path.splitext(file)
        if ext == ".xlsx":
            stub_content += f"    {file_name}: BytesIO\n"
stub_content += "\ntemplates: Templates"

with open(os.path.join(dir_, "__init__.pyi"), "w") as f:
    f.write(stub_content)

templates = Templates()
__all__ = ["templates"]
