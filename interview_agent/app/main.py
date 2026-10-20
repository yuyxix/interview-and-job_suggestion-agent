import sys

#   Windows 专有坑（必须放在其它导入之前）：
#   psycopg 的异步模式不支持 ProactorEventLoop，只认 SelectorEventLoop。
#   uvicorn 0.38 在 Windows 下（未开 reload / workers 时）会显式返回
#   ProactorEventLoop，单靠 asyncio.set_event_loop_policy() 是压不住的，
#   所以这里再把 uvicorn 的 loop factory 也替换成 Selector。
if sys.platform == 'win32':
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def _selector_loop_factory(use_subprocess: bool = False):
        return asyncio.SelectorEventLoop

    try:
        import uvicorn.loops.asyncio as _uvicorn_async_loops
        import uvicorn.loops.auto as _uvicorn_auto_loops

        _uvicorn_async_loops.asyncio_loop_factory = _selector_loop_factory
        _uvicorn_auto_loops.auto_loop_factory = _selector_loop_factory
    except Exception as e:
        print(f'[startup] 替换 uvicorn 事件循环工厂失败: {type(e).__name__}: {e}')

import chromadb
from fastapi import FastAPI
from app.web.chat_router.chat_router import (
    chat_router, vosk_router, history_router, profile_router,
)
from fastapi.staticfiles import StaticFiles
import os
import uvicorn
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from app.ai.agent.multi_agent.graph.exam_graph import ExamGraph
from app.web.default_page_router.default_page_router import default_Page_roter
from app.web.system_router.system_router import system_router
# checkpointer：从 InMemorySaver（进程内存，重启就丢）换成 PG（持久化）
# 想回退就把下面这四行换回 from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from app.ai.agent.multi_agent.memory.manage import memory_manager
import redis.asyncio as redis
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

# 读取配置文件（Redis 的地址/密码/库号都在 .env 里）
load_dotenv()


# 定义异步上下文管理器
@asynccontextmanager
async def content_manager(app: FastAPI):
    # === checkpointer：PG 持久化（重启 / 改代码后多轮状态不丢）===
    # 连接参数和 langgraph 官方 from_conn_string 保持一致：autocommit + prepare_threshold=0 + dict_row
    pg_pool = AsyncConnectionPool(
        conninfo=os.getenv('POSTGRESQL_URL'),
        min_size=2,
        max_size=10,
        open=False,
        kwargs={'autocommit': True, 'prepare_threshold': 0, 'row_factory': dict_row},
    )
    await pg_pool.open()
    # saver 必须在事件循环里构造（它内部会 get_running_loop）
    memory = AsyncPostgresSaver(pg_pool)
    await memory.setup()        # 建 checkpoints 等表，幂等，重复启动也不会出事

    # 创建redis：必须带上密码，库号等参数也从 .env 读
    r = redis.StrictRedis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', 6379)),
        db=int(os.getenv('REDIS_DB', 3)),
        password=os.getenv('REDIS_PASSWORD'),
    )
    # 预加载向量数据库
    vector_path = os.getenv('CHROMA_PATH')
    embed_fn = SentenceTransformerEmbeddingFunction(
        model_name=r"E:\models\paraphrase-multilingual-MiniLM-L12-v2"
    )
    client = chromadb.PersistentClient(vector_path)

    # 创建集合
    app.state.collection = client.get_or_create_collection(
        name='long_memory',
        embedding_function=embed_fn
    )
    app.state.exam_agent = ExamGraph(memory, r)
    # 注册向量库：让图节点里（拿不到 Request）也能用记忆
    memory_manager.set_collection(app.state.collection)

    # 预加载 Vosk 语音模型：避免第一次点语音时再等模型加载。
    # 加载失败不阻塞主服务，语音功能会在第一次连接时再尝试。
    try:
        from app.ai.agent.vosk_agent import VoskAgent
        await asyncio.to_thread(VoskAgent.get_vosk)
        print('Vosk 语音模型预加载完成')
    except Exception as e:
        print(f'Vosk 语音模型预加载失败: {type(e).__name__}: {e}')

    print('AI模拟面试智能体创建成功')
    # 销毁对象
    yield
    app.state.exam_agent = None
    await pg_pool.close()
    print('AI模拟面试智能体销毁成功')


app = FastAPI(lifespan=content_manager)
# 注册路由
app.include_router(chat_router)
app.include_router(vosk_router)
app.include_router(history_router)     # 前端拉历史对话
app.include_router(profile_router)     # 前端查看 / 编辑用户画像
app.include_router(default_Page_roter)
app.include_router(system_router)      # 登录 / 注册 / 管理
app.mount('/static', StaticFiles(directory='./html'), name='static')

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000)