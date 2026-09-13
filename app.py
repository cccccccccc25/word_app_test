import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import time
from database import DatabaseManager
from learning import LearningManager
from file_import import import_words_from_file

class WordApp:
    def __init__(self, root):
        self.root = root
        self.root.title("记单词App")
        self.root.geometry("800x600")
        
        # 初始化数据库和学习管理器
        self.db = DatabaseManager()
        self.lm = LearningManager()
        
        # 创建主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标签页
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建单词库标签页
        self.word_list_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.word_list_tab, text="单词库")
        
        # 创建学习标签页
        self.learn_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.learn_tab, text="学习")
        
        # 创建复习标签页
        self.review_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.review_tab, text="复习")
        
        # 创建熟悉单词标签页
        self.familiar_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.familiar_tab, text="熟悉单词")
        
        # 创建不熟悉单词标签页
        self.unfamiliar_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.unfamiliar_tab, text="不熟悉单词")
        
        # 创建统计标签页
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="统计")
        
        # 初始化各个标签页
        self.init_word_list_tab()
        self.init_learn_tab()
        self.init_review_tab()
        self.init_familiar_tab()
        self.init_unfamiliar_tab()
        self.init_stats_tab()
        
        # 刷新单词列表
        self.refresh_word_list()
    
    def init_word_list_tab(self):
        """初始化单词库标签页"""
        # 创建添加单词区域
        add_frame = ttk.LabelFrame(self.word_list_tab, text="添加单词")
        add_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(add_frame, text="单词:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.word_entry = ttk.Entry(add_frame, width=30)
        self.word_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="释义:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.meaning_entry = ttk.Entry(add_frame, width=50)
        self.meaning_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(add_frame, text="例句:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.example_entry = ttk.Entry(add_frame, width=50)
        self.example_entry.grid(row=2, column=1, padx=5, pady=5)
        
        add_button = ttk.Button(add_frame, text="添加", command=self.add_word)
        add_button.grid(row=3, column=1, padx=5, pady=10, sticky=tk.E)
        
        import_button = ttk.Button(add_frame, text="从文件导入", command=self.import_words)
        import_button.grid(row=3, column=2, padx=5, pady=10, sticky=tk.E)
        
        # 创建搜索区域
        search_frame = ttk.LabelFrame(self.word_list_tab, text="搜索")
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(search_frame, text="关键词:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        search_button = ttk.Button(search_frame, text="搜索", command=self.search_words)
        search_button.grid(row=0, column=2, padx=5, pady=5)
        
        refresh_button = ttk.Button(search_frame, text="刷新", command=self.refresh_word_list)
        refresh_button.grid(row=0, column=3, padx=5, pady=5)
        
        # 创建单词列表
        list_frame = ttk.LabelFrame(self.word_list_tab, text="单词列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建树状视图
        columns = ("id", "word", "meaning", "example")
        self.word_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        self.word_tree.heading("id", text="ID")
        self.word_tree.heading("word", text="单词")
        self.word_tree.heading("meaning", text="释义")
        self.word_tree.heading("example", text="例句")
        
        # 设置列宽
        self.word_tree.column("id", width=50)
        self.word_tree.column("word", width=100)
        self.word_tree.column("meaning", width=200)
        self.word_tree.column("example", width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.word_tree.yview)
        self.word_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.word_tree.pack(fill=tk.BOTH, expand=True)

        # # 创建操作按钮
        # button_frame = ttk.Frame(self.word_list_tab)
        # button_frame.pack(fill=tk.X, padx=10, pady=10)
        #
        # edit_button = ttk.Button(button_frame, text="编辑", command=self.edit_word)
        # edit_button.pack(side=tk.LEFT, padx=5)
        #
        # delete_button = ttk.Button(button_frame, text="删除选中", command=self.delete_word)
        # delete_button.pack(side=tk.LEFT, padx=5)
        #
        # clear_button = ttk.Button(button_frame, text="清空单词库", command=self.clear_word_list)
        # clear_button.pack(side=tk.LEFT, padx=5)
    
    def init_learn_tab(self):
        """初始化学习标签页"""
        # 创建学习设置
        settings_frame = ttk.LabelFrame(self.learn_tab, text="学习设置")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(settings_frame, text="单词数量:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.learn_limit_var = tk.StringVar(value="10")
        ttk.Entry(settings_frame, textvariable=self.learn_limit_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        start_learn_button = ttk.Button(settings_frame, text="开始学习", command=self.start_learning)
        start_learn_button.grid(row=0, column=2, padx=5, pady=5)
        
        # 创建学习区域
        self.learn_content_frame = ttk.LabelFrame(self.learn_tab, text="学习内容")
        self.learn_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 单词显示
        self.word_label = ttk.Label(self.learn_content_frame, text="", font=("Arial", 36))
        self.word_label.pack(pady=40)
        
        self.meaning_label = ttk.Label(self.learn_content_frame, text="", font=("Arial", 18))
        self.meaning_label.pack(pady=10)
        
        self.example_label = ttk.Label(self.learn_content_frame, text="", font=("Arial", 14), foreground="#666")
        self.example_label.pack(pady=10)
        
        # 熟悉/不熟悉按钮
        self.learn_options_frame = ttk.Frame(self.learn_content_frame)
        self.learn_options_frame.pack(pady=20)
        
        self.learn_familiar_button = ttk.Button(self.learn_options_frame, text="熟悉", command=self.learn_mark_familiar, state=tk.DISABLED)
        self.learn_familiar_button.pack(side=tk.LEFT, padx=20)
        
        self.learn_unfamiliar_button = ttk.Button(self.learn_options_frame, text="不熟悉", command=self.learn_mark_unfamiliar, state=tk.DISABLED)
        self.learn_unfamiliar_button.pack(side=tk.LEFT, padx=20)
        
        # 学习状态
        self.current_learn_word = None
    

    
    def init_review_tab(self):
        """初始化复习标签页"""
        # 创建复习设置
        settings_frame = ttk.LabelFrame(self.review_tab, text="复习设置")
        settings_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(settings_frame, text="单词数量:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.review_limit_var = tk.StringVar(value="10")
        ttk.Entry(settings_frame, textvariable=self.review_limit_var, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        start_review_button = ttk.Button(settings_frame, text="开始复习", command=self.start_review)
        start_review_button.grid(row=0, column=2, padx=5, pady=5)
        
        # 创建复习区域
        self.review_content_frame = ttk.LabelFrame(self.review_tab, text="复习内容")
        self.review_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 单词显示
        self.review_word_label = ttk.Label(self.review_content_frame, text="", font=("Arial", 36))
        self.review_word_label.pack(pady=40)
        
        # 内容显示区域
        self.review_details_frame = ttk.Frame(self.review_content_frame)
        self.review_details_frame.pack(pady=10)
        
        self.review_meaning_label = ttk.Label(self.review_details_frame, text="", font=("Arial", 18))
        self.review_meaning_label.pack(pady=10)
        
        self.review_example_label = ttk.Label(self.review_details_frame, text="", font=("Arial", 14), foreground="#666")
        self.review_example_label.pack(pady=10)
        
        # 选项按钮区域
        self.review_options_frame = ttk.Frame(self.review_content_frame)
        self.review_options_frame.pack(pady=20)
        
        self.familiar_button = ttk.Button(self.review_options_frame, text="熟悉", command=self.mark_familiar, state=tk.DISABLED)
        self.familiar_button.pack(side=tk.LEFT, padx=20)
        
        self.unfamiliar_button = ttk.Button(self.review_options_frame, text="不熟悉", command=self.mark_unfamiliar, state=tk.DISABLED)
        self.unfamiliar_button.pack(side=tk.LEFT, padx=20)
        
        # 复习状态
        self.current_review_word = None
    
    def init_stats_tab(self):
        """初始化统计标签页"""
        stats_frame = ttk.LabelFrame(self.stats_tab, text="学习统计")
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.stats_text = tk.Text(stats_frame, wrap=tk.WORD, font=("Arial", 14))
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        refresh_stats_button = ttk.Button(stats_frame, text="刷新统计", command=self.refresh_stats)
        refresh_stats_button.pack(pady=10)
        
        # 初始刷新统计
        self.refresh_stats()
    
    def init_familiar_tab(self):
        """初始化熟悉单词标签页"""
        # 创建熟悉单词列表
        list_frame = ttk.LabelFrame(self.familiar_tab, text="熟悉单词列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建树状视图
        columns = ("id", "word", "meaning", "example")
        self.familiar_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        self.familiar_tree.heading("id", text="ID")
        self.familiar_tree.heading("word", text="单词")
        self.familiar_tree.heading("meaning", text="释义")
        self.familiar_tree.heading("example", text="例句")
        
        # 设置列宽
        self.familiar_tree.column("id", width=50)
        self.familiar_tree.column("word", width=100)
        self.familiar_tree.column("meaning", width=200)
        self.familiar_tree.column("example", width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.familiar_tree.yview)
        self.familiar_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.familiar_tree.pack(fill=tk.BOTH, expand=True)
        
        # 创建操作按钮
        button_frame = ttk.Frame(self.familiar_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        refresh_button = ttk.Button(button_frame, text="刷新", command=self.refresh_familiar_list)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 初始刷新熟悉单词列表
        self.refresh_familiar_list()
    
    def init_unfamiliar_tab(self):
        """初始化不熟悉单词标签页"""
        # 创建不熟悉单词列表
        list_frame = ttk.LabelFrame(self.unfamiliar_tab, text="不熟悉单词列表")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建树状视图
        columns = ("id", "word", "meaning", "example")
        self.unfamiliar_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # 设置列标题
        self.unfamiliar_tree.heading("id", text="ID")
        self.unfamiliar_tree.heading("word", text="单词")
        self.unfamiliar_tree.heading("meaning", text="释义")
        self.unfamiliar_tree.heading("example", text="例句")
        
        # 设置列宽
        self.unfamiliar_tree.column("id", width=50)
        self.unfamiliar_tree.column("word", width=100)
        self.unfamiliar_tree.column("meaning", width=200)
        self.unfamiliar_tree.column("example", width=300)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.unfamiliar_tree.yview)
        self.unfamiliar_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.unfamiliar_tree.pack(fill=tk.BOTH, expand=True)
        
        # 创建操作按钮
        button_frame = ttk.Frame(self.unfamiliar_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        refresh_button = ttk.Button(button_frame, text="刷新", command=self.refresh_unfamiliar_list)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # 初始刷新不熟悉单词列表
        self.refresh_unfamiliar_list()
    
    def add_word(self):
        """添加单词"""
        word = self.word_entry.get().strip()
        meaning = self.meaning_entry.get().strip()
        example = self.example_entry.get().strip()
        
        if not word or not meaning:
            messagebox.showerror("错误", "单词和释义不能为空")
            return
        
        if self.db.add_word(word, meaning, example):
            messagebox.showinfo("成功", "单词添加成功")
            self.refresh_word_list()
            # 清空输入框
            self.word_entry.delete(0, tk.END)
            self.meaning_entry.delete(0, tk.END)
            self.example_entry.delete(0, tk.END)
        else:
            messagebox.showerror("错误", "单词添加失败")
    
    def refresh_word_list(self):
        """刷新单词列表"""
        # 清空树状视图
        for item in self.word_tree.get_children():
            self.word_tree.delete(item)
        
        # 获取所有新单词
        words = self.db.get_words_by_status('new')
        for word in words:
            self.word_tree.insert("", tk.END, values=word)
    
    def refresh_familiar_list(self):
        """刷新熟悉单词列表"""
        # 清空树状视图
        for item in self.familiar_tree.get_children():
            self.familiar_tree.delete(item)
        
        # 获取熟悉单词
        words = self.db.get_words_by_status('familiar')
        for word in words:
            self.familiar_tree.insert("", tk.END, values=word)
    
    def refresh_unfamiliar_list(self):
        """刷新不熟悉单词列表"""
        # 清空树状视图
        for item in self.unfamiliar_tree.get_children():
            self.unfamiliar_tree.delete(item)
        
        # 获取不熟悉单词
        words = self.db.get_words_by_status('unfamiliar')
        for word in words:
            self.unfamiliar_tree.insert("", tk.END, values=word)
    
    def search_words(self):
        """搜索单词"""
        keyword = self.search_entry.get().strip()
        if not keyword:
            self.refresh_word_list()
            return
        
        # 清空树状视图
        for item in self.word_tree.get_children():
            self.word_tree.delete(item)
        
        # 搜索单词
        words = self.db.search_words(keyword)
        for word in words:
            self.word_tree.insert("", tk.END, values=word)
    
    # def edit_word(self):
    #     """编辑单词"""
    #     selected_item = self.word_tree.selection()
    #     if not selected_item:
    #         messagebox.showerror("错误", "请选择要编辑的单词")
    #         return
    #
    #     item = selected_item[0]
    #     word_data = self.word_tree.item(item, "values")
    #
    #     # 创建编辑窗口
    #     edit_window = tk.Toplevel(self.root)
    #     edit_window.title("编辑单词")
    #     edit_window.geometry("500x300")
    #
    #     ttk.Label(edit_window, text="单词:").grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
    #     word_var = tk.StringVar(value=word_data[1])
    #     ttk.Entry(edit_window, textvariable=word_var, width=30).grid(row=0, column=1, padx=10, pady=10)
    #
    #     ttk.Label(edit_window, text="释义:").grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
    #     meaning_var = tk.StringVar(value=word_data[2])
    #     ttk.Entry(edit_window, textvariable=meaning_var, width=50).grid(row=1, column=1, padx=10, pady=10)
    #
    #     ttk.Label(edit_window, text="例句:").grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)
    #     example_var = tk.StringVar(value=word_data[3] if word_data[3] else "")
    #     ttk.Entry(edit_window, textvariable=example_var, width=50).grid(row=2, column=1, padx=10, pady=10)
    #
    #     def save_changes():
    #         word = word_var.get().strip()
    #         meaning = meaning_var.get().strip()
    #         example = example_var.get().strip()
    #
    #         if not word or not meaning:
    #             messagebox.showerror("错误", "单词和释义不能为空")
    #             return
    #
    #         if self.db.update_word(word_data[0], word, meaning, example):
    #             messagebox.showinfo("成功", "单词更新成功")
    #             self.refresh_word_list()
    #             edit_window.destroy()
    #         else:
    #             messagebox.showerror("错误", "单词更新失败")
    #
    #     save_button = ttk.Button(edit_window, text="保存", command=save_changes)
    #     save_button.grid(row=3, column=1, padx=10, pady=20, sticky=tk.E)
    #
    # def delete_word(self):
    #     """删除选中的单词"""
    #     selected_items = self.word_tree.selection()
    #     if not selected_items:
    #         messagebox.showerror("错误", "请选择要删除的单词")
    #         return
    #
    #     count = len(selected_items)
    #     if messagebox.askyesno("确认", f"确定要删除选中的 {count} 个单词吗？"):
    #         success_count = 0
    #         for item in selected_items:
    #             word_data = self.word_tree.item(item, "values")
    #             if self.db.delete_word(word_data[0]):
    #                 success_count += 1
    #
    #         if success_count > 0:
    #             messagebox.showinfo("成功", f"成功删除 {success_count} 个单词")
    #             self.refresh_word_list()
    #         else:
    #             messagebox.showerror("错误", "单词删除失败")
    #
    # def clear_word_list(self):
    #     """清空单词库"""
    #     if messagebox.askyesno("确认", "确定要清空整个单词库吗？此操作不可恢复！"):
    #         try:
    #             # 获取所有单词
    #             words = self.db.get_all_words()
    #             success_count = 0
    #             for word in words:
    #                 if self.db.delete_word(word[0]):
    #                     success_count += 1
    #
    #             if success_count > 0:
    #                 messagebox.showinfo("成功", f"成功清空单词库，删除了 {success_count} 个单词")
    #                 self.refresh_word_list()
    #             else:
    #                 messagebox.showinfo("提示", "单词库已经是空的")
    #         except Exception as e:
    #             messagebox.showerror("错误", f"清空单词库失败: {e}")
    
    def import_words(self):
        """从文件导入单词"""
        # 打开文件选择对话框
        file_path = filedialog.askopenfilename(
            title="选择要导入的文件",
            filetypes=[
                ("所有文件", "*.*"),
                ("文本文件", "*.txt"),
                ("PDF文件", "*.pdf")
            ]
        )
        
        if not file_path:
            return
        
        # 导入单词
        try:
            count = import_words_from_file(file_path)
            if count > 0:
                messagebox.showinfo("成功", f"成功导入 {count} 个单词")
                self.refresh_word_list()
            else:
                messagebox.showinfo("提示", "没有导入任何单词，请检查文件格式")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败: {e}")
    
    def start_learning(self):
        """开始学习"""
        try:
            limit = int(self.learn_limit_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        # 开始学习会话
        self.lm.start_learning_session('learn', limit)
        
        if not self.lm.current_words:
            messagebox.showinfo("提示", "单词库为空，请先添加单词")
            return
        
        # 重置学习状态
        self.current_learn_word = None
        
        # 更新学习界面
        self.update_learn_ui()
        
        # 启用按钮
        self.learn_familiar_button.config(state=tk.NORMAL)
        self.learn_unfamiliar_button.config(state=tk.NORMAL)
    
    def update_learn_ui(self):
        """更新学习界面"""
        word = self.lm.get_current_word()
        if word:
            self.current_learn_word = word
            self.word_label.config(text=word[1])
            self.meaning_label.config(text=word[2])
            self.example_label.config(text=word[3] if word[3] else "无例句")
        else:
            self.current_learn_word = None
            self.word_label.config(text="学习完成")
            self.meaning_label.config(text="")
            self.example_label.config(text="")
            self.learn_familiar_button.config(state=tk.DISABLED)
            self.learn_unfamiliar_button.config(state=tk.DISABLED)
    

    
    def learn_mark_familiar(self):
        """标记单词为熟悉"""
        if self.current_learn_word:
            # 记录学习结果（正确）
            self.lm.record_learning(self.current_learn_word[0], True)
            # 移动到下一个单词
            if not self.lm.next_word():
                # 学习完成
                self.update_learn_ui()
                messagebox.showinfo("提示", "本轮单词已经全部学习完！")
            else:
                self.update_learn_ui()
    
    def learn_mark_unfamiliar(self):
        """标记单词为不熟悉"""
        if self.current_learn_word:
            # 记录学习结果（错误）
            self.lm.record_learning(self.current_learn_word[0], False)
            # 移动到下一个单词
            if not self.lm.next_word():
                # 学习完成
                self.update_learn_ui()
                messagebox.showinfo("提示", "本轮单词已经全部学习完！")
            else:
                self.update_learn_ui()
    

    
    def start_review(self):
        """开始复习"""
        try:
            limit = int(self.review_limit_var.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        # 开始复习会话
        self.lm.start_learning_session('review', limit)
        
        if not self.lm.current_words:
            messagebox.showinfo("提示", "没有需要复习的单词")
            return
        
        # 重置复习状态
        self.current_review_word = None
        
        # 更新复习界面
        self.update_review_ui()
        
        # 启用选项按钮
        self.familiar_button.config(state=tk.NORMAL)
        self.unfamiliar_button.config(state=tk.NORMAL)
    
    def update_review_ui(self):
        """更新复习界面"""
        word = self.lm.get_current_word()
        if word:
            self.current_review_word = word
            # 显示英文单词
            self.review_word_label.config(text=word[1])
            # 显示中文释义和例句
            self.review_meaning_label.config(text=word[2])
            self.review_example_label.config(text=word[3] if word[3] else "无例句")
        else:
            self.review_word_label.config(text="复习完成")
            self.review_meaning_label.config(text="")
            self.review_example_label.config(text="")
            self.familiar_button.config(state=tk.DISABLED)
            self.unfamiliar_button.config(state=tk.DISABLED)
    

    
    def mark_familiar(self):
        """标记单词为熟悉"""
        if self.current_review_word:
            # 记录学习结果（正确）
            self.lm.record_learning(self.current_review_word[0], True)
            # 移动到下一个单词
            if not self.lm.next_word():
                # 复习完成
                self.update_review_ui()
                messagebox.showinfo("提示", "本轮单词已经全部复习完！")
            else:
                self.update_review_ui()
    
    def mark_unfamiliar(self):
        """标记单词为不熟悉"""
        if self.current_review_word:
            # 记录学习结果（错误）
            self.lm.record_learning(self.current_review_word[0], False)
            # 移动到下一个单词
            if not self.lm.next_word():
                # 复习完成
                self.update_review_ui()
                messagebox.showinfo("提示", "本轮单词已经全部复习完！")
            else:
                self.update_review_ui()
    
    def refresh_stats(self):
        """刷新统计信息"""
        stats = self.lm.get_learning_stats()
        self.stats_text.delete(1.0, tk.END)
        self.stats_text.insert(tk.END, stats)
    
    def __del__(self):
        """清理资源"""
        self.db.close()
        self.lm.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = WordApp(root)
    root.mainloop()