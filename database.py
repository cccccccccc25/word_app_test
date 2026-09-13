import sqlite3
import os

class DatabaseManager:
    _instance = None
    
    def __new__(cls, db_path='words.db'):
        """单例模式，避免重复连接数据库"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.db_path = db_path
            cls._instance.conn = None
            cls._instance.cursor = None
            cls._instance._init_database()
        return cls._instance
    
    def _init_database(self):
        """初始化数据库，创建必要的表"""
        try:
            # 连接数据库
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # 创建单词表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT UNIQUE NOT NULL,
                    meaning TEXT NOT NULL,
                    example TEXT,
                    difficulty INTEGER DEFAULT 1,
                    status TEXT DEFAULT 'new', -- new, familiar, unfamiliar
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建学习记录表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word_id INTEGER,
                    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    correct BOOLEAN,
                    FOREIGN KEY (word_id) REFERENCES words (id)
                )
            ''')
            
            # 创建学习统计信息表
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS learning_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_words INTEGER DEFAULT 0,
                    learned_words INTEGER DEFAULT 0,
                    last_study_date TIMESTAMP
                )
            ''')
            
            # 重置统计信息
            self.cursor.execute('DELETE FROM learning_stats')
            self.cursor.execute('INSERT INTO learning_stats (total_words, learned_words) VALUES (0, 0)')
            
            self.conn.commit()
            print("数据库初始化成功")
        except Exception as e:
            print(f"数据库初始化失败: {e}")
    
    def add_word(self, word, meaning, example=None):
        """添加新单词，重复的单词不会被添加"""
        try:
            # 检查数据库是否为空
            self.cursor.execute('SELECT COUNT(*) FROM words')
            count = self.cursor.fetchone()[0]
            if count == 0:
                # 重置序列，确保从1开始
                self.cursor.execute('DELETE FROM sqlite_sequence WHERE name="words"')
            
            # 使用 INSERT OR IGNORE 确保重复的单词不会被添加，并明确设置status为'new'
            self.cursor.execute(
                'INSERT OR IGNORE INTO words (word, meaning, example, status) VALUES (?, ?, ?, ?)',
                (word, meaning, example, 'new')
            )
            # 检查是否成功插入（不是重复的）
            if self.cursor.rowcount > 0:
                self.conn.commit()
                # 更新统计信息
                self._update_stats()
                return True
            else:
                # 单词已存在，不添加
                print(f"单词 '{word}' 已存在，跳过添加")
                return False
        except Exception as e:
            print(f"添加单词失败: {e}")
            return False
    
    def get_all_words(self):
        """获取所有单词"""
        try:
            self.cursor.execute('SELECT * FROM words ORDER BY id')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取单词失败: {e}")
            return []
    
    def get_words_by_status(self, status):
        """根据状态获取单词"""
        try:
            self.cursor.execute('SELECT * FROM words WHERE status = ? ORDER BY id', (status,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取单词失败: {e}")
            return []
    
    def update_word_status(self, word_id, status):
        """更新单词状态"""
        try:
            self.cursor.execute(
                'UPDATE words SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?',
                (status, word_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新单词状态失败: {e}")
            return False
    
    def update_word_status_to_end(self, word_id, status):
        """更新单词状态并移到对应状态列表的最后"""
        try:
            # 开始事务
            # 先更新状态
            self.cursor.execute(
                'UPDATE words SET status = ?, last_updated = CURRENT_TIMESTAMP WHERE id = ?',
                (status, word_id)
            )
            
            # 重新编号以确保顺序
            self._renumber_word_ids()
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新单词状态失败: {e}")
            return False
    
    def search_words(self, keyword):
        """搜索单词"""
        try:
            self.cursor.execute(
                'SELECT * FROM words WHERE word LIKE ? OR meaning LIKE ?',
                (f'%{keyword}%', f'%{keyword}%')
            )
            return self.cursor.fetchall()
        except Exception as e:
            print(f"搜索单词失败: {e}")
            return []
    
    def update_word(self, word_id, word, meaning, example=None):
        """更新单词信息"""
        try:
            self.cursor.execute(
                'UPDATE words SET word=?, meaning=?, example=? WHERE id=?',
                (word, meaning, example, word_id)
            )
            self.conn.commit()
            return True
        except Exception as e:
            print(f"更新单词失败: {e}")
            return False
    
    def delete_word(self, word_id):
        """删除单词并重新编号ID"""
        try:
            # 先删除相关的学习记录
            self.cursor.execute('DELETE FROM learning_records WHERE word_id=?', (word_id,))
            # 再删除单词
            self.cursor.execute('DELETE FROM words WHERE id=?', (word_id,))
            
            # 重新编号ID，确保从1开始
            self._renumber_word_ids()
            
            self.conn.commit()
            # 更新统计信息
            self._update_stats()
            return True
        except Exception as e:
            print(f"删除单词失败: {e}")
            return False
    
    def _renumber_word_ids(self):
        """重新编号单词ID，确保不熟悉的单词在最后"""
        try:
            # 获取所有单词并按状态和最后更新时间排序
            # 顺序：familiar -> new -> unfamiliar（不熟悉的在最后）
            self.cursor.execute('''
                SELECT id, word, meaning, example, difficulty, status, added_date, last_updated 
                FROM words 
                ORDER BY 
                    CASE 
                        WHEN status = 'familiar' THEN 1
                        WHEN status = 'new' THEN 2
                        WHEN status = 'unfamiliar' THEN 3
                        ELSE 4
                    END, 
                    last_updated ASC
            ''')
            words = self.cursor.fetchall()
            
            if not words:
                return
            
            # 清空原表
            self.cursor.execute('DELETE FROM words')
            
            # 重新插入并指定ID
            for i, word in enumerate(words, 1):
                self.cursor.execute('''
                    INSERT INTO words (id, word, meaning, example, difficulty, status, added_date, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (i, word[1], word[2], word[3], word[4], word[5], word[6], word[7]))
            
            # 重置序列
            self.cursor.execute('DELETE FROM sqlite_sequence WHERE name="words"')
            
        except Exception as e:
            print(f"重新编号失败: {e}")
    
    def add_learning_record(self, word_id, correct):
        """添加学习记录"""
        try:
            self.cursor.execute(
                'INSERT INTO learning_records (word_id, correct) VALUES (?, ?)',
                (word_id, correct)
            )
            self.conn.commit()
            # 更新统计信息
            self._update_stats()
            return True
        except Exception as e:
            print(f"添加学习记录失败: {e}")
            return False
    
    def get_learning_stats(self):
        """获取学习统计信息"""
        try:
            self.cursor.execute('SELECT * FROM learning_stats LIMIT 1')
            return self.cursor.fetchone()
        except Exception as e:
            print(f"获取学习统计信息失败: {e}")
            return None
    
    def _update_stats(self):
        """更新学习统计信息"""
        try:
            # 更新总单词数
            self.cursor.execute('SELECT COUNT(*) FROM words')
            total_words = self.cursor.fetchone()[0]
            
            # 更新已学习单词数（至少有一条学习记录的单词）
            self.cursor.execute('SELECT COUNT(DISTINCT word_id) FROM learning_records')
            learned_words = self.cursor.fetchone()[0]
            
            # 更新统计信息
            self.cursor.execute(
                'UPDATE learning_stats SET total_words=?, learned_words=?, last_study_date=CURRENT_TIMESTAMP',
                (total_words, learned_words)
            )
            self.conn.commit()
        except Exception as e:
            print(f"更新统计信息失败: {e}")
    
    def get_words_for_review(self, limit=10):
        """获取需要复习的单词"""
        try:
            # 优先选择最近学习但错误的单词，然后选择未学习的单词
            self.cursor.execute('''
                SELECT w.* FROM words w
                LEFT JOIN learning_records lr ON w.id = lr.word_id
                GROUP BY w.id
                ORDER BY 
                    CASE 
                        WHEN MAX(CASE WHEN lr.correct = 0 THEN lr.review_date END) IS NOT NULL 
                        THEN MAX(CASE WHEN lr.correct = 0 THEN lr.review_date END)
                        ELSE '1970-01-01'
                    END DESC,
                    (SELECT COUNT(*) FROM learning_records WHERE word_id = w.id) ASC
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()
        except Exception as e:
            print(f"获取复习单词失败: {e}")
            return []
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

# # 测试数据库功能
# if __name__ == "__main__":
#     db = DatabaseManager()
#
#     # 测试添加单词
#     db.add_word("apple", "苹果", "I eat an apple every day.")
#     db.add_word("banana", "香蕉", "Bananas are yellow.")
#     db.add_word("cat", "猫", "The cat is cute.")
#
#     # 测试获取所有单词
#     print("所有单词:")
#     for word in db.get_all_words():
#         print(word)
#
#     # 测试搜索单词
#     print("\n搜索单词 'a':")
#     for word in db.search_words("a"):
#         print(word)
#
#     # 测试添加学习记录
#     db.add_learning_record(1, True)
#     db.add_learning_record(2, False)
#
#     # 测试获取学习统计信息
#     print("\n学习统计信息:")
#     stats = db.get_learning_stats()
#     print(stats)
#
#     # 测试获取复习单词
#     print("\n需要复习的单词:")
#     for word in db.get_words_for_review():
#         print(word)
#
#     db.close()