import os

class Parser:
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.filename, self.file_extension = os.path.splitext(file_path)
        