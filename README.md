# 记单词应用

基于 Python 的记单词桌面应用（Tkinter GUI + Flask API + SQLite），支持单词管理、学习、复习、统计与文件导入。

## 技术栈

Python / Tkinter / Flask / SQLite / Pytest / Requests

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动桌面应用（GUI）
python app.py

# 或启动 API 服务（默认 5000 端口）
python api.py

# 3. 运行接口自动化测试（自动使用独立测试库，不影响真实数据）
pytest tests/ -v
```

## 目录结构

```
word_app/
├── app.py           # Tkinter 桌面端
├── api.py           # Flask API 服务（被测对象）
├── database.py      # SQLite 数据访问层
├── learning.py      # 学习/复习业务逻辑
├── file_import.py   # 文件导入
├── tests/           # 接口自动化测试
│   ├── conftest.py  # 测试环境配置（自动启动服务 + 数据隔离）
│   └── test_api.py  # 接口测试用例
└── requirements.txt
```

## API 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/health | 健康检查 |
| GET | /api/words | 单词列表（支持 status/keyword 参数） |
| GET | /api/words/{id} | 查询单个单词 |
| POST | /api/words | 新增单词 |
| PUT | /api/words/{id} | 更新单词 |
| DELETE | /api/words/{id} | 删除单词 |
| POST | /api/learning/start | 开始学习 |
| POST | /api/learning/mark | 标记学习结果 |
| POST | /api/review/start | 开始复习 |
| POST | /api/review/mark | 标记复习结果 |
| GET | /api/stats | 学习统计 |

## 测试说明

- 测试运行时会自动创建独立的 `test_words.db`，**不会污染真实单词数据**
- 通过 `DB_PATH` 环境变量实现测试数据隔离
- 已覆盖：单词增删改查、异常参数、重复数据、学习/复习流程、统计接口
