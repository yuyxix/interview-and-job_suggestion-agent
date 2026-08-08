from langchain_chroma import Chroma
from ai import LoadEmbeddingModel
import os
from dotenv import load_dotenv
load_dotenv()


def load_chroma_con():
    # 创建检索器对象
    return Chroma(
        collection_name=os.getenv('COLLECTION_NAME'),
        persist_directory=os.getenv('CHROMA_PATH'),
        embedding_function=LoadEmbeddingModel.load_embedding_model(),
    )