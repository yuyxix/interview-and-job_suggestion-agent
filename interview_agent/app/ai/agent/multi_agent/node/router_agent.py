from langchain.agents import create_agent
from app.ai.agent.multi_agent.schema.intention_schema import RouterSchema
from app.ai.model.my_model import MyModel
from app.ai.prompt.prompt_builder import BuilderPromptYaml
from langchain.agents.middleware import ModelCallLimitMiddleware
'''
    路由分类节点
'''
# 读取提示词文件
prompt = BuilderPromptYaml.get_prompt("router_agent.yaml")


def router_agent(question):
    try:
        # 用本地模型做意图识别
        model = MyModel.get_local_model()
        # 创建智能体
        agent = create_agent(
            model=model,
            system_prompt=prompt,
            response_format=RouterSchema,
            middleware=[
                ModelCallLimitMiddleware(
                    thread_limit=3,
                    exit_behavior='end'
                )
            ]
        )
        # 提问
        user_msg = {'messages': {'role': 'user', 'content': question}}
        rs = agent.invoke(user_msg)
        # 把输出结果转换成字典或者json
        data = rs['structured_response'].model_dump()
        return data.get('router', 'chat')
    except Exception as e:
        print('切换模型兜底')
        try:
            # 用本地模型做意图识别
            model = MyModel.get_model()
            # 创建智能体
            agent = create_agent(
                model=model,
                system_prompt=prompt,
                response_format=RouterSchema,
                middleware=[
                    ModelCallLimitMiddleware(
                        thread_limit=3,
                        exit_behavior='end'
                    )
                ]
            )
            # 提问
            user_msg = {'messages': {'role': 'user', 'content': question}}
            rs = agent.invoke(user_msg)
            # 把输出结果转换成字典或者json
            data = rs['structured_response'].model_dump()
            return data.get('router', 'chat')
        except Exception as e:
            print('手动兜底')
            return 'chat'