#!/usr/bin/env python3
"""
文件导入模块，支持从文本文件和PDF文件导入单词
"""

import os
import re
from database import DatabaseManager

# 尝试导入PDF处理库
try:
    import PyPDF2
    has_pdf = True
except ImportError:
    has_pdf = False

def extract_words_from_text(file_path):
    """从文本文件中提取单词
    只提取单词和中文释义，忽略例句
    """
    words = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # 使用 split() 处理所有空白字符（空格、tab等）
            parts = line.split()
            if len(parts) >= 2:
                word = parts[0]
                # 找到第一个中文字符的位置
                meaning_start = None
                for i, part in enumerate(parts[1:]):
                    if any('\u4e00' <= c <= '\u9fff' for c in part):
                        meaning_start = i + 1
                        break

                if meaning_start is not None:
                    # 提取中文释义（包含所有中文部分）
                    meaning_parts = []
                    for part in parts[meaning_start:]:
                        if any('\u4e00' <= c <= '\u9fff' for c in part):
                            meaning_parts.append(part)
                        else:
                            # 遇到非中文字符，停止提取释义
                            break

                    if meaning_parts:
                        meaning = ' '.join(meaning_parts)
                        if word and meaning:
                            words.append((word, meaning, None))
    except Exception as e:
        print(f"读取文本文件失败: {e}")

    return words

def extract_words_from_pdf(file_path):
    """从PDF文件中提取单词
    只提取单词和中文释义，忽略例句
    """
    if not has_pdf:
        print("PyPDF2库未安装，无法处理PDF文件")
        return []
    
    words = []
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                # 提取文本并处理编码
                page_text = page.extract_text()
                if page_text:
                    # 尝试不同的编码处理
                    try:
                        # 尝试UTF-8编码
                        text += page_text + '\n'
                    except UnicodeDecodeError:
                        # 尝试其他编码
                        try:
                            text += page_text.encode('latin-1').decode('utf-8', errors='ignore') + '\n'
                        except:
                            text += page_text.encode('latin-1').decode('gbk', errors='ignore') + '\n'
            
        # 处理PDF文本，提取单词和中文释义
        lines = text.split('\n')
        current_word = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试多种方式提取单词
            # 1. 检查是否是单词行（包含音标）
            word_match = re.match(r'^([a-zA-Z]+)\s*[/(].*?[/)]$', line)
            if word_match:
                # 开始新单词
                current_word = word_match.group(1)
                continue
            
            # 2. 直接尝试从行中提取单词和中文
            # 检查是否包含英文单词和中文
            if any(c.isalpha() for c in line) and any('\u4e00' <= c <= '\u9fff' for c in line):
                # 尝试分割单词和中文
                parts = line.split()  # 使用 split() 处理所有空白字符
                word = None
                meaning_start = None
                
                for i, part in enumerate(parts):
                    if part.isalpha() and not word:
                        word = part
                    elif any('\u4e00' <= c <= '\u9fff' for c in part):
                        meaning_start = i
                        break
                
                if word and meaning_start is not None:
                    # 提取中文释义
                    meaning_parts = []
                    for part in parts[meaning_start:]:
                        if any('\u4e00' <= c <= '\u9fff' for c in part):
                            meaning_parts.append(part)
                    
                    if meaning_parts:
                        meaning = ' '.join(meaning_parts)
                        words.append((word, meaning, None))
                    continue
            
            # 3. 检查是否是释义行（包含中文）
            if current_word and any('\u4e00' <= c <= '\u9fff' for c in line):
                # 提取中文释义，去掉词性部分
                meaning = ''
                # 找到第一个中文字符的位置
                for i, c in enumerate(line):
                    if '\u4e00' <= c <= '\u9fff':
                        meaning = line[i:].strip()
                        break
                
                if meaning:
                    words.append((current_word, meaning, None))
                    current_word = None
    except Exception as e:
        print(f"读取PDF文件失败: {e}")
    
    return words

def import_words_from_file(file_path, db_path='words.db'):
    """从文件导入单词到数据库，重复的单词不会被添加"""
    if not os.path.exists(file_path):
        print(f"文件不存在: {file_path}")
        return 0
    
    # 根据文件扩展名选择提取方法
    ext = os.path.splitext(file_path)[1].lower()
    if ext in ['.txt', '.text']:
        words = extract_words_from_text(file_path)
    elif ext == '.pdf' and has_pdf:
        words = extract_words_from_pdf(file_path)
    else:
        print(f"不支持的文件格式: {ext}")
        return 0
    
    if not words:
        print("没有提取到单词，请检查文件格式")
        return 0
    
    print(f"成功提取 {len(words)} 个单词")
    
    # 导入到数据库
    # 注意：由于单例模式，这里会使用已有的数据库连接
    db = DatabaseManager(db_path)
    count = 0
    total = len(words)
    print(f"开始导入 {total} 个单词...")
    
    for i, (word, meaning, example) in enumerate(words):
        if word and meaning:
            # 确保单词和释义不为空
            word = word.strip()
            meaning = meaning.strip()
            if word and meaning:
                if db.add_word(word, meaning, example):
                    count += 1
                    if i % 10 == 0:  # 每10个单词打印一次进度
                        print(f"已导入 {count}/{total} 个单词...")
                else:
                    # 跳过重复单词
                    pass
    
    print(f"导入完成: 成功 {count} 个，跳过 {total - count} 个")
    return count