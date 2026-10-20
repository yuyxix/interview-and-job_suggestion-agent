from vosk import Model, KaldiRecognizer
import pyaudio
import json
from dotenv import load_dotenv
import os
import time

load_dotenv()


def test():
    # 模型路径
    model_path = os.getenv('VOSK_PATH')
    # 加载模型
    model = Model(model_path=model_path)
    # 加载本地音频配置
    p = pyaudio.PyAudio()

    stream = p.open(
        format=pyaudio.paInt16,   # 十六位整数格式
        channels=1,   # 单声道
        rate=16000,   # 16kHz采样率
        input=True,   # 输入模式(录音)
        frames_per_buffer=8000    # 每个缓冲区4096帧
    )
    # 加载音频配置，获取vosk识别器
    re = KaldiRecognizer(model, 16000)
    # 提示用户开始说话
    print('开始说话')
    # 开始音频
    stream.start_stream()
    # 开始识别
    while True:
        data = re.AcceptWaveform(stream.read(4096))
        if data:
            # print(f'{re.Result()}')
            # 类型转换
            rs = json.loads(re.Result())
            if rs['text']:
                print(f'用户说的话:{rs['text']}')


if __name__ == '__main__':
    test()
