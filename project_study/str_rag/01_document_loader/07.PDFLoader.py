import os
from langchain_community.document_loaders import PyPDFLoader

base_path = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(base_path, 'datasets', '09.算力租赁.pdf')

def pdf_loader(file_path):
    loader = PyPDFLoader(file_path)
    data = loader.load()
    return data

if __name__ == '__main__':
    data = pdf_loader(file_path)
    for item in data:
        print(item.page_content)

