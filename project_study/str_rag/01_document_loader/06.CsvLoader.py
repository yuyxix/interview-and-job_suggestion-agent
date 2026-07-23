from langchain_community.document_loaders import CSVLoader
import os

base_path = os.path.dirname(os.path.dirname(__file__))
file_path = os.path.join(base_path, 'datasets', 'guazi.csv')

def csv_loader(file_path):
    csv = CSVLoader(
        file_path = file_path,
        encoding = 'utf-8',
        csv_args = {'delimiter': '\t'}
    )
    data = csv.load()
    return data

if __name__ == '__main__':
    cs = csv_loader(file_path)
    print(cs)


