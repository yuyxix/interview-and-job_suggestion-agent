import os
import yaml


class BuilderPromptYaml:
    _prompt = None
    # 定义静态函数
    @staticmethod
    def get_prompt(file_name):
        # 用这种方法，获取文件位置更加稳定
        current_path = os.path.dirname(os.path.abspath(__file__))
        yaml_path = os.path.join(current_path, file_name)
        with open(yaml_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        # 构建提示词
        BuilderPromptYaml._prompt = f"""
                --角色: {config['role']}\n
                --任务: {"\n".join(config['task'])}\n
                --规则: {"\n".join(config['rules'])}\n
                --输出: {"\n".join(config['output'])}\n
                --示例: {config['examples']}\n
                """
        return BuilderPromptYaml._prompt.replace(' ', '')
if __name__ == '__main__':
    a = BuilderPromptYaml.get_prompt('send_email_agent.yaml')
    print(a)