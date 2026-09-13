import random
from database import DatabaseManager

class LearningManager:
    def __init__(self, db_path='words.db'):
        self.db = DatabaseManager(db_path)
        self.current_words = []
        self.current_index = 0
        self.test_results = []
    
    def get_words_for_learning(self, limit=10):
        """获取用于学习的单词（从新单词库）"""
        words = self.db.get_words_by_status('new')
        if len(words) > limit:
            return random.sample(words, limit)
        return words
    
    def get_words_for_test(self, limit=10):
        """获取用于测试的单词（从新单词库）"""
        words = self.db.get_words_by_status('new')
        if len(words) > limit:
            return random.sample(words, limit)
        return words
    
    def get_words_for_review(self, limit=10):
        """获取用于复习的单词（从不熟悉单词库）"""
        words = self.db.get_words_by_status('unfamiliar')
        if len(words) > limit:
            return random.sample(words, limit)
        return words
    
    def start_learning_session(self, mode='learn', limit=10):
        """开始学习会话"""
        if mode == 'learn':
            self.current_words = self.get_words_for_learning(limit)
        elif mode == 'test':
            self.current_words = self.get_words_for_test(limit)
        elif mode == 'review':
            self.current_words = self.get_words_for_review(limit)
        else:
            self.current_words = []
        
        self.current_index = 0
        self.test_results = []
        return self.current_words
    
    def get_current_word(self):
        """获取当前单词"""
        if self.current_index < len(self.current_words):
            return self.current_words[self.current_index]
        return None
    
    def next_word(self):
        """移动到下一个单词"""
        if self.current_index < len(self.current_words) - 1:
            self.current_index += 1
            return True
        return False
    
    def previous_word(self):
        """移动到上一个单词"""
        if self.current_index > 0:
            self.current_index -= 1
            return True
        return False
    
    def record_learning(self, word_id, correct):
        """记录学习结果并更新单词状态"""
        self.db.add_learning_record(word_id, correct)
        if correct:
            self.test_results.append('正确')
            # 标记为熟悉
            self.db.update_word_status(word_id, 'familiar')
        else:
            self.test_results.append('错误')
            # 标记为不熟悉并移到不熟悉单词表的最后
            self.db.update_word_status_to_end(word_id, 'unfamiliar')
    
    def get_test_results(self):
        """获取测试结果"""
        if not self.test_results:
            return "暂无测试结果"
        
        total = len(self.test_results)
        correct = self.test_results.count('正确')
        accuracy = (correct / total) * 100 if total > 0 else 0
        
        result = f"测试结果:\n"
        result += f"总题数: {total}\n"
        result += f"正确: {correct}\n"
        result += f"错误: {total - correct}\n"
        result += f"正确率: {accuracy:.1f}%"
        
        return result
    
    def get_learning_stats(self):
        """获取学习统计信息"""
        stats = self.db.get_learning_stats()
        if not stats:
            return "暂无统计信息"
        
        result = f"学习统计:\n"
        result += f"总单词数: {stats[1]}\n"
        result += f"已学习单词数: {stats[2]}\n"
        result += f"学习进度: {stats[2]}/{stats[1]}\n"
        if stats[3]:
            result += f"最后学习时间: {stats[3]}\n"
        
        return result
    
    # def generate_test_options(self, correct_word):
    #     """生成测试选项"""
    #     all_words = self.db.get_all_words()
    #     # 过滤掉当前单词
    #     other_words = [w for w in all_words if w[0] != correct_word[0]]
    #
    #     # 随机选择3个其他单词作为错误选项
    #     if len(other_words) >= 3:
    #         wrong_options = random.sample(other_words, 3)
    #     else:
    #         # 如果单词不够，重复使用
    #         wrong_options = other_words * (3 // len(other_words) + 1)[:3]
    #
    #     # 构建选项列表
    #     options = [correct_word[2]]  # 正确选项
    #     for word in wrong_options:
    #         options.append(word[2])  # 错误选项
    #
    #     # 随机打乱选项顺序
    #     random.shuffle(options)
    #
    #     # 找到正确选项的索引
    #     correct_index = options.index(correct_word[2])
    #
    #     return options, correct_index
    #
    # def close(self):
    #     """关闭数据库连接"""
    #     self.db.close()

# 测试学习模块
if __name__ == "__main__":
    lm = LearningManager()
    
    # 测试学习模式
    print("=== 学习模式 ===")
    lm.start_learning_session('learn', 3)
    for i in range(3):
        word = lm.get_current_word()
        print(f"单词: {word[1]}")
        print(f"释义: {word[2]}")
        if word[3]:
            print(f"例句: {word[3]}")
        print()
        lm.next_word()
    
    # # 测试测试模式
    # print("=== 测试模式 ===")
    # lm.start_learning_session('test', 3)
    # for i in range(3):
    #     word = lm.get_current_word()
    #     print(f"单词: {word[1]}")
    #     options, correct_index = lm.generate_test_options(word)
    #     for j, option in enumerate(options):
    #         print(f"{j+1}. {option}")
    #     # 模拟用户选择
    #     user_choice = random.randint(0, 3)
    #     print(f"用户选择: {user_choice+1}")
    #     print(f"正确答案: {correct_index+1}")
    #     lm.record_learning(word[0], user_choice == correct_index)
    #     print()
    #     lm.next_word()
    #
    # # 测试测试结果
    # print("=== 测试结果 ===")
    # print(lm.get_test_results())
    # print()
    #
    # 测试学习统计
    # print("=== 学习统计 ===")
    # print(lm.get_learning_stats())
    # print()
    #
    # # 测试复习模式
    # print("=== 复习模式 ===")
    # lm.start_learning_session('review', 3)
    # for i in range(len(lm.current_words)):
    #     word = lm.get_current_word()
    #     print(f"单词: {word[1]}")
    #     print(f"释义: {word[2]}")
    #     print()
    #     lm.next_word()
    #
    # lm.close()