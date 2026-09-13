import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import DatabaseManager
from learning import LearningManager
from file_import import import_words_from_file

app = Flask(__name__)
CORS(app)

# 支持通过环境变量 DB_PATH 指定数据库路径（测试时隔离数据，默认仍用 words.db）
db = DatabaseManager(os.environ.get('DB_PATH', 'words.db'))
lm = LearningManager(os.environ.get('DB_PATH', 'words.db'))

@app.route('/api/words', methods=['GET'])
def get_words():
    """获取单词列表"""
    status = request.args.get('status', None)
    keyword = request.args.get('keyword', None)
    
    if keyword:
        words = db.search_words(keyword)
    elif status:
        words = db.get_words_by_status(status)
    else:
        words = db.get_all_words()
    
    result = []
    for word in words:
        result.append({
            'id': word[0],
            'word': word[1],
            'meaning': word[2],
            'example': word[3] if word[3] else '',
            'status': word[5],
            'added_date': word[6],
            'last_updated': word[7]
        })
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': result
    })

@app.route('/api/words/<int:word_id>', methods=['GET'])
def get_word(word_id):
    """获取单个单词"""
    words = db.get_all_words()
    for word in words:
        if word[0] == word_id:
            return jsonify({
                'code': 200,
                'message': 'success',
                'data': {
                    'id': word[0],
                    'word': word[1],
                    'meaning': word[2],
                    'example': word[3] if word[3] else '',
                    'status': word[5],
                    'added_date': word[6],
                    'last_updated': word[7]
                }
            })
    
    return jsonify({
        'code': 404,
        'message': '单词不存在',
        'data': None
    })

@app.route('/api/words', methods=['POST'])
def add_word():
    """添加单词"""
    data = request.get_json()
    if not data or 'word' not in data or 'meaning' not in data:
        return jsonify({
            'code': 400,
            'message': '参数错误，单词和释义不能为空',
            'data': None
        })
    
    word = data['word'].strip()
    meaning = data['meaning'].strip()
    example = data.get('example', '').strip()
    
    if not word or not meaning:
        return jsonify({
            'code': 400,
            'message': '单词和释义不能为空',
            'data': None
        })
    
    if db.add_word(word, meaning, example):
        return jsonify({
            'code': 200,
            'message': '添加成功',
            'data': {
                'word': word,
                'meaning': meaning,
                'example': example
            }
        })
    else:
        return jsonify({
            'code': 409,
            'message': '单词已存在',
            'data': None
        })

@app.route('/api/words/<int:word_id>', methods=['PUT'])
def update_word(word_id):
    """更新单词"""
    data = request.get_json()
    if not data:
        return jsonify({
            'code': 400,
            'message': '参数错误',
            'data': None
        })
    
    word = data.get('word', '').strip()
    meaning = data.get('meaning', '').strip()
    example = data.get('example', '').strip()
    
    if word and meaning:
        if db.update_word(word_id, word, meaning, example):
            return jsonify({
                'code': 200,
                'message': '更新成功',
                'data': {
                    'id': word_id,
                    'word': word,
                    'meaning': meaning,
                    'example': example
                }
            })
        else:
            return jsonify({
                'code': 500,
                'message': '更新失败',
                'data': None
            })
    else:
        return jsonify({
            'code': 400,
            'message': '单词和释义不能为空',
            'data': None
        })

@app.route('/api/words/<int:word_id>', methods=['DELETE'])
def delete_word(word_id):
    """删除单词"""
    if db.delete_word(word_id):
        return jsonify({
            'code': 200,
            'message': '删除成功',
            'data': {
                'id': word_id
            }
        })
    else:
        return jsonify({
            'code': 500,
            'message': '删除失败',
            'data': None
        })

@app.route('/api/words/batch', methods=['DELETE'])
def batch_delete_words():
    """批量删除单词"""
    data = request.get_json()
    if not data or 'ids' not in data:
        return jsonify({
            'code': 400,
            'message': '参数错误',
            'data': None
        })
    
    ids = data['ids']
    success_count = 0
    for word_id in ids:
        if db.delete_word(word_id):
            success_count += 1
    
    return jsonify({
        'code': 200,
        'message': f'成功删除 {success_count} 个单词',
        'data': {
            'total': len(ids),
            'success': success_count
        }
    })

@app.route('/api/words/import', methods=['POST'])
def import_words():
    """从文件导入单词"""
    if 'file' not in request.files:
        return jsonify({
            'code': 400,
            'message': '请选择要导入的文件',
            'data': None
        })
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({
            'code': 400,
            'message': '请选择要导入的文件',
            'data': None
        })
    
    try:
        import os
        import tempfile
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as f:
            file.save(f.name)
            temp_path = f.name
        
        count = import_words_from_file(temp_path)
        
        os.unlink(temp_path)
        
        if count > 0:
            return jsonify({
                'code': 200,
                'message': f'成功导入 {count} 个单词',
                'data': {
                    'count': count
                }
            })
        else:
            return jsonify({
                'code': 400,
                'message': '没有导入任何单词，请检查文件格式',
                'data': None
            })
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'导入失败: {str(e)}',
            'data': None
        })

@app.route('/api/learning/start', methods=['POST'])
def start_learning():
    """开始学习"""
    data = request.get_json()
    limit = data.get('limit', 10)
    
    lm.start_learning_session('learn', limit)
    
    if not lm.current_words:
        return jsonify({
            'code': 400,
            'message': '单词库为空，请先添加单词',
            'data': None
        })
    
    word = lm.get_current_word()
    return jsonify({
        'code': 200,
        'message': '开始学习',
        'data': {
            'total': len(lm.current_words),
            'current': lm.current_index + 1,
            'word': {
                'id': word[0],
                'word': word[1],
                'meaning': word[2],
                'example': word[3] if word[3] else ''
            }
        }
    })

@app.route('/api/learning/next', methods=['POST'])
def next_learning_word():
    """下一个单词"""
    if lm.next_word():
        word = lm.get_current_word()
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total': len(lm.current_words),
                'current': lm.current_index + 1,
                'word': {
                    'id': word[0],
                    'word': word[1],
                    'meaning': word[2],
                    'example': word[3] if word[3] else ''
                }
            }
        })
    else:
        return jsonify({
            'code': 400,
            'message': '已经是最后一个单词',
            'data': None
        })

@app.route('/api/learning/mark', methods=['POST'])
def mark_learning_word():
    """标记学习单词"""
    data = request.get_json()
    word_id = data.get('word_id')
    familiar = data.get('familiar', True)
    
    if word_id is None:
        return jsonify({
            'code': 400,
            'message': '参数错误',
            'data': None
        })
    
    lm.record_learning(word_id, familiar)
    
    finished = not lm.next_word()
    
    if finished:
        return jsonify({
            'code': 200,
            'message': '学习完成',
            'data': {
                'finished': True,
                'word': None
            }
        })
    
    word = lm.get_current_word()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'finished': False,
            'total': len(lm.current_words),
            'current': lm.current_index + 1,
            'word': {
                'id': word[0],
                'word': word[1],
                'meaning': word[2],
                'example': word[3] if word[3] else ''
            }
        }
    })

@app.route('/api/review/start', methods=['POST'])
def start_review():
    """开始复习"""
    data = request.get_json()
    limit = data.get('limit', 10)
    
    lm.start_learning_session('review', limit)
    
    if not lm.current_words:
        return jsonify({
            'code': 400,
            'message': '没有需要复习的单词',
            'data': None
        })
    
    word = lm.get_current_word()
    return jsonify({
        'code': 200,
        'message': '开始复习',
        'data': {
            'total': len(lm.current_words),
            'current': lm.current_index + 1,
            'word': {
                'id': word[0],
                'word': word[1],
                'meaning': word[2],
                'example': word[3] if word[3] else ''
            }
        }
    })

@app.route('/api/review/next', methods=['POST'])
def next_review_word():
    """下一个复习单词"""
    if lm.next_word():
        word = lm.get_current_word()
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total': len(lm.current_words),
                'current': lm.current_index + 1,
                'word': {
                    'id': word[0],
                    'word': word[1],
                    'meaning': word[2],
                    'example': word[3] if word[3] else ''
                }
            }
        })
    else:
        return jsonify({
            'code': 400,
            'message': '已经是最后一个单词',
            'data': None
        })

@app.route('/api/review/mark', methods=['POST'])
def mark_review_word():
    """标记复习单词"""
    data = request.get_json()
    word_id = data.get('word_id')
    familiar = data.get('familiar', True)
    
    if word_id is None:
        return jsonify({
            'code': 400,
            'message': '参数错误',
            'data': None
        })
    
    lm.record_learning(word_id, familiar)
    
    finished = not lm.next_word()
    
    if finished:
        return jsonify({
            'code': 200,
            'message': '复习完成',
            'data': {
                'finished': True,
                'word': None
            }
        })
    
    word = lm.get_current_word()
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'finished': False,
            'total': len(lm.current_words),
            'current': lm.current_index + 1,
            'word': {
                'id': word[0],
                'word': word[1],
                'meaning': word[2],
                'example': word[3] if word[3] else ''
            }
        }
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取学习统计"""
    stats = lm.get_learning_stats()
    
    if not stats:
        return jsonify({
            'code': 200,
            'message': 'success',
            'data': {
                'total_words': 0,
                'learned_words': 0,
                'last_study_date': None
            }
        })
    
    return jsonify({
        'code': 200,
        'message': 'success',
        'data': {
            'total_words': stats[1],
            'learned_words': stats[2],
            'last_study_date': stats[3]
        }
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        'code': 200,
        'message': 'OK',
        'data': {
            'status': 'running'
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)