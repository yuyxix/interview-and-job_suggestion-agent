from FlagEmbedding import FlagReranker
import os
from dotenv import load_dotenv
load_dotenv()


def load_rerank_model():
    return FlagReranker(
        model_name_or_path=os.getenv('RERANKER_MODEL_PATH'),
        use_fp16=True
    )