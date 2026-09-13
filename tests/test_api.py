"""记单词应用接口自动化测试用例（pytest + requests）

覆盖模块：
- 单词管理：新增 / 查询 / 更新 / 删除 / 搜索 / 异常参数
- 学习流程：开始学习 / 标记结果
- 复习流程：开始复习
- 统计：学习统计
"""
import uuid

import requests

BASE_URL = 'http://127.0.0.1:5000'


def unique_word():
    """生成唯一测试单词，避免与真实数据冲突"""
    return f'test_{uuid.uuid4().hex[:6]}'


def get_word_id(word):
    """根据单词名查 ID"""
    r = requests.get(f'{BASE_URL}/api/words')
    for item in r.json()['data']:
        if item['word'] == word:
            return item['id']
    return None


# ========== 健康检查 ==========

def test_health():
    r = requests.get(f'{BASE_URL}/api/health')
    assert r.status_code == 200
    assert r.json()['code'] == 200
    assert r.json()['data']['status'] == 'running'


# ========== 单词管理 ==========

def test_add_word():
    """正常新增单词"""
    word = unique_word()
    r = requests.post(f'{BASE_URL}/api/words', json={'word': word, 'meaning': '测试释义'})
    assert r.status_code == 200
    body = r.json()
    assert body['code'] == 200
    assert body['data']['word'] == word
    assert body['data']['meaning'] == '测试释义'


def test_add_word_missing_meaning():
    """缺失必填字段：释义为空应报参数错误"""
    r = requests.post(f'{BASE_URL}/api/words', json={'word': unique_word(), 'meaning': '  '})
    assert r.json()['code'] == 400


def test_add_duplicate_word():
    """重复添加同一单词应返回 409"""
    word = unique_word()
    requests.post(f'{BASE_URL}/api/words', json={'word': word, 'meaning': '释义1'})
    r = requests.post(f'{BASE_URL}/api/words', json={'word': word, 'meaning': '释义2'})
    assert r.json()['code'] == 409
    assert '已存在' in r.json()['message']


def test_get_word():
    """新增后能通过 ID 查询到完整字段"""
    word = unique_word()
    requests.post(f'{BASE_URL}/api/words', json={'word': word, 'meaning': '释义'})
    word_id = get_word_id(word)
    r = requests.get(f'{BASE_URL}/api/words/{word_id}')
    body = r.json()
    assert body['code'] == 200
    assert body['data']['word'] == word
    assert body['data']['meaning'] == '释义'


def test_get_word_not_found():
    """查询不存在的单词应返回 404"""
    r = requests.get(f'{BASE_URL}/api/words/999999')
    assert r.json()['code'] == 404


def test_update_word():
    """更新单词释义"""
    word = unique_word()
    requests.post(f'{BASE_URL}/api/words', json={'word': word, 'meaning': '原释义'})
    word_id = get_word_id(word)
    r = requests.put(f'{BASE_URL}/api/words/{word_id}', json={'word': word, 'meaning': '新释义'})
    assert r.json()['code'] == 200
    assert r.json()['data']['meaning'] == '新释义'
    # 再次查询确认已更新
    r2 = requests.get(f'{BASE_URL}/api/words/{word_id}')
    assert r2.json()['data']['meaning'] == '新释义'


def test_delete_word():
    """删除单词后再次查询应返回 404"""
    word = unique_word()
    requests.post(f'{BASE_URL}/api/words', json={'word': word, 'meaning': '释义'})
    word_id = get_word_id(word)
    r = requests.delete(f'{BASE_URL}/api/words/{word_id}')
    assert r.json()['code'] == 200
    r2 = requests.get(f'{BASE_URL}/api/words/{word_id}')
    assert r2.json()['code'] == 404


def test_search_words():
    """关键词搜索"""
    word = unique_word()
    requests.post(f'{BASE_URL}/api/words', json={'word': word, 'meaning': '独特释义'})
    r = requests.get(f'{BASE_URL}/api/words', params={'keyword': word})
    words = [item['word'] for item in r.json()['data']]
    assert word in words


# ========== 学习流程 ==========

def test_learning_flow():
    """开始学习 → 标记结果 → 学习完成"""
    word = unique_word()
    requests.post(f'{BASE_URL}/api/words', json={'word': word, 'meaning': '释义'})
    word_id = get_word_id(word)

    r = requests.post(f'{BASE_URL}/api/learning/start', json={'limit': 10})
    assert r.json()['code'] == 200
    assert r.json()['data']['total'] >= 1

    r = requests.post(f'{BASE_URL}/api/learning/mark', json={'word_id': word_id, 'familiar': True})
    assert r.json()['code'] == 200
    assert r.json()['data']['finished'] is True  # 只有一个单词，标记后本轮结束


def test_review_flow():
    """标记为不熟悉后，复习接口能拉到该单词"""
    word = unique_word()
    requests.post(f'{BASE_URL}/api/words', json={'word': word, 'meaning': '释义'})
    word_id = get_word_id(word)

    # 学习时标记为不熟悉
    requests.post(f'{BASE_URL}/api/learning/start', json={'limit': 10})
    r = requests.post(f'{BASE_URL}/api/learning/mark', json={'word_id': word_id, 'familiar': False})
    assert r.json()['code'] == 200

    # 复习会话应包含该单词
    r = requests.post(f'{BASE_URL}/api/review/start', json={'limit': 10})
    assert r.json()['code'] == 200
    assert r.json()['data']['total'] >= 1


# ========== 统计 ==========

def test_stats():
    """学习统计接口返回结构正确"""
    r = requests.get(f'{BASE_URL}/api/stats')
    assert r.status_code == 200
    assert r.json()['code'] == 200
    assert 'total_words' in r.json()['data']
    assert 'learned_words' in r.json()['data']
