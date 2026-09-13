"""pytest 全局配置：启动被测服务 + 测试数据隔离"""
import os
import sys
import time
import threading

import requests
import pytest

# 测试使用独立数据库，绝不污染真实 words.db（必须在 import api 之前设置）
TEST_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'test_words.db')
os.environ['DB_PATH'] = TEST_DB

# 把项目根目录加入模块搜索路径，才能 import api
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

BASE_URL = 'http://127.0.0.1:5000'


@pytest.fixture(scope='session', autouse=True)
def start_server():
    """启动 Flask 被测服务（后台线程），测试结束自动关闭"""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)  # 每次测试从干净库开始（必须先删库再 import api，否则连接占用文件）

    from api import app  # noqa: E402

    server = threading.Thread(
        target=app.run,
        kwargs={'host': '127.0.0.1', 'port': 5000, 'debug': False, 'use_reloader': False},
        daemon=True
    )
    server.start()
    # 轮询健康检查，等服务真正就绪
    for _ in range(20):
        try:
            requests.get(f'{BASE_URL}/api/health', timeout=1)
            break
        except Exception:
            time.sleep(0.5)
    yield


@pytest.fixture(autouse=True)
def cleanup():
    """每个测试结束后，清理本次产生的 test_ 前缀数据，保证用例互不干扰"""
    yield
    r = requests.get(f'{BASE_URL}/api/words')
    for item in r.json().get('data', []):
        if item['word'].startswith('test_'):
            requests.delete(f'{BASE_URL}/api/words/{item["id"]}')
