from langchain_community.document_loaders import UnstructuredMarkdownLoader
import os
import markdown

base_path = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(base_path, 'datasets', '09.算力租赁.md')

def md_loader(file_path):
    md = UnstructuredMarkdownLoader(
        file_path = file_path,
        mode = 'elements'
    )
    data = md.load()
    return data

if __name__ == '__main__':
    md = md_loader(file_path)
    for item in md:
        print(item.page_content)