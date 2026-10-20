import os
import yaml


class BuilderPromptYaml:
    @staticmethod
    def _render(value) -> str:
        """把 YAML 里的任意结构渲染成文本

        兼容三种写法：
          - 字符串
          - 字符串列表（原来的写法）
          - 字典 / 字典列表（summary_agent.yaml、profile_agent.yaml 用的写法）

        原来的实现直接 chr(10).join(config['output'])，遇到字典就会报
        TypeError: sequence item 0: expected str instance, dict found，
        导致摘要和画像 Agent 初始化失败，画像一直生成不出来。
        """
        if value is None:
            return ''
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return '\n'.join(BuilderPromptYaml._render(item) for item in value)
        if isinstance(value, dict):
            return '\n'.join(
                f'{key}：{BuilderPromptYaml._render(val)}'
                for key, val in value.items()
            )
        return str(value)

    @staticmethod
    def get_prompt(file_name: str) -> str:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, file_name)
        with open(file_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        prompt = (
            f"一 角色：{BuilderPromptYaml._render(config.get('role', ''))}\n"
            f"二 任务：\n{BuilderPromptYaml._render(config.get('task', []))}\n"
            f"三 规则：\n{BuilderPromptYaml._render(config.get('rule', []))}\n"
            f"四 输出：\n{BuilderPromptYaml._render(config.get('output', []))}\n"
            f"五 实例：\n{BuilderPromptYaml._render(config.get('example', []))}\n"
        )
        return prompt.strip()


if __name__ == '__main__':
    b = BuilderPromptYaml()
    prom = b.get_prompt(r"E:\workspace\interview_agent\app\ai\prompt\intention_node.yaml")
    print(prom)