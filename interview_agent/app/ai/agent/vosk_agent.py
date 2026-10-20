import json
import re
import threading

from fastapi import WebSocket, WebSocketDisconnect
from vosk import KaldiRecognizer

from app.ai.model.my_model import MyModel


def _normalize_text(text: str) -> str:
    """Vosk 中文模型会在汉字之间输出空格，展示前去掉

    '你好 我 想 找 一 份 后端 开发 的 工作' → '你好我想找一份后端开发的工作'
    英文单词之间、以及英文和数字内部的空格保留。
    """
    text = (text or '').strip()
    text = re.sub(r'(?<=[一-鿿])\s+(?=[一-鿿])', '', text)
    text = re.sub(r'(?<=[一-鿿])\s+(?=[A-Za-z0-9])', '', text)
    text = re.sub(r'(?<=[A-Za-z0-9])\s+(?=[一-鿿])', '', text)
    return text


class VoskAgent:
    """Vosk 语音识别

    浏览器负责采集麦克风音频，按 16kHz / 单声道 / Int16 PCM 通过 WebSocket
    发给这里；服务端不再直接打开本机麦克风（pyaudio 已移除）。
    这样部署到其它机器时，识别的是访问者自己的麦克风。
    """

    _vosk = None
    _lock = threading.Lock()

    def __init__(self):
        # 模型加载较慢，get_vosk() 用单例复用
        self.model = MyModel.get_vosk_model()

    @staticmethod
    def get_vosk():
        # 启动预加载和第一次语音请求可能同时发生，加锁避免重复加载模型
        if VoskAgent._vosk is None:
            with VoskAgent._lock:
                if VoskAgent._vosk is None:
                    VoskAgent._vosk = VoskAgent()
        return VoskAgent._vosk

    async def vosk_chat(self, ws: WebSocket, accepted: bool = False):
        if not accepted:
            await ws.accept()

        rec = KaldiRecognizer(self.model, 16000)
        last_partial = ''

        try:
            while True:
                message = await ws.receive()
                if message.get('type') == 'websocket.disconnect':
                    break

                data = message.get('bytes')
                if not data:
                    continue

                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result() or '{}')
                    text = _normalize_text(result.get('text'))
                    if text:
                        await ws.send_json({'type': 'final', 'text': text})
                        last_partial = ''
                else:
                    result = json.loads(rec.PartialResult() or '{}')
                    partial = _normalize_text(result.get('partial'))
                    if partial and partial != last_partial:
                        last_partial = partial
                        await ws.send_json({'type': 'partial', 'text': partial})
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f'[vosk] 识别异常: {type(e).__name__}: {e}')
            try:
                await ws.send_json({'type': 'error', 'message': '语音识别失败，请重试'})
            except Exception:
                pass
        finally:
            try:
                result = json.loads(rec.FinalResult() or '{}')
                text = _normalize_text(result.get('text'))
                if text:
                    await ws.send_json({'type': 'final', 'text': text})
            except Exception:
                pass
            try:
                await ws.close()
            except Exception:
                pass

