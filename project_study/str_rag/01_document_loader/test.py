import os
from pathlib import Path
from docx import Document

# print(base_path)
# data = os.path.join(base_path, 'datasets', '华清远见.txt')
# print(data)

# base_path = Path(os.path.dirname(__file__))
# print(base_path.parent)
base_path = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(base_path, 'datasets', 'test.docx')

doc = Document(file_path)
table = doc.tables
print(table)
a = []
for item in table:
    for i in item.rows:
        print(i.cells)
        for i in i.cells:
            print(i.text)
print(a)

