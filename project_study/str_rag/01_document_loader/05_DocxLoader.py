from docx import Document
import os

base_path = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(base_path, 'datasets', 'test.docx')

data = []

def doc_loader(file_path):
    doc = Document(file_path)
    for  table in doc.tables:
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                row_data.append(cell)
            data.append(row_data)
    return data


if __name__ == '__main__':
    docs = doc_loader(file_path)
    print(docs)