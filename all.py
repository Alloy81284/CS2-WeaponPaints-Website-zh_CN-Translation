#!/usr/bin/env python3
import os
import sys
import json
import time
from datetime import datetime

# 导入所有翻译器模块
try:
    from agents import AgentTranslator
    from keychains import KeychainTranslator
    from music import MusicKitTranslator
    from skins import SkinGloveTranslator
    from stickers import StickerTranslator
except ImportError as e:
    print(f"错误: 无法导入翻译器模块 - {e}")
    print("请确保所有翻译器文件(agents.py, keychains.py, music_kits.py, skins.py, stickers.py)位于同一目录。")
    sys.exit(1)

# 配置
INPUT_DIR = "."  # 默认在当前目录寻找JSON文件
OUTPUT_DIR = "translated"  # 输出文件目录
LOG_DIR = "logs"  # 日志目录
CACHE_DIR = "translation_cache"  # 翻译缓存目录

# 确保目录存在
for directory in [OUTPUT_DIR, LOG_DIR, CACHE_DIR]:
    os.makedirs(directory, exist_ok=True)

def get_log_file():
    """生成日志文件名"""
    return os.path.join(LOG_DIR, f"translation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

def log_message(message, log_file):
    """记录日志到文件和控制台"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def save_translated_data(data, output_file):
    """保存翻译后的数据到文件"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def translate_agents(log_file):
    """翻译探员数据"""
    input_file = os.path.join(INPUT_DIR, "agents.json")
    output_file = os.path.join(OUTPUT_DIR, "agents.json")
    
    if not os.path.exists(input_file):
        log_message(f"错误: 找不到探员输入文件 {input_file}", log_file)
        return False
    
    log_message("开始翻译探员数据...", log_file)
    
    # 初始化探员翻译器
    translator = AgentTranslator()
    if not translator.load_translations():
        log_message("探员翻译器初始化失败", log_file)
        return False
    
    translator.build_index()
    
    # 读取输入文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            log_message(f"错误: 探员文件格式不正确，应为JSON数组", log_file)
            return False
        
        # 翻译
        translated_count = 0
        total_count = len(data)
        
        for i, item in enumerate(data):
            original_name = item.get('agent_name', '')
            translated_item = translator.translate_item(item)
            
            # 检查是否翻译成功
            if translated_item.get('agent_name', '') != original_name:
                translated_count += 1
            
            # 更新原始数据
            data[i] = translated_item
        
        # 保存结果
        save_translated_data(data, output_file)
        
        log_message(f"✓ 探员翻译完成: {translated_count}/{total_count} 项已翻译", log_file)
        return True
        
    except Exception as e:
        log_message(f"✗ 探员翻译失败: {str(e)}", log_file)
        return False

def translate_keychains(log_file):
    """翻译钥匙扣数据"""
    input_file = os.path.join(INPUT_DIR, "keychains.json")
    output_file = os.path.join(OUTPUT_DIR, "keychains.json")
    
    if not os.path.exists(input_file):
        log_message(f"错误: 找不到钥匙扣输入文件 {input_file}", log_file)
        return False
    
    log_message("开始翻译钥匙扣数据...", log_file)
    
    # 初始化钥匙扣翻译器
    translator = KeychainTranslator()
    if not translator.load_translations():
        log_message("钥匙扣翻译器初始化失败", log_file)
        return False
    
    translator.build_index()
    
    # 读取输入文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            log_message(f"错误: 钥匙扣文件格式不正确，应为JSON数组", log_file)
            return False
        
        # 翻译
        translated_count = 0
        total_count = len(data)
        
        for i, item in enumerate(data):
            original_name = item.get('name', '')
            translated_item = translator.translate_item(item)
            
            # 检查是否翻译成功
            if translated_item.get('name', '') != original_name:
                translated_count += 1
            
            # 更新原始数据
            data[i] = translated_item
        
        # 保存结果
        save_translated_data(data, output_file)
        
        log_message(f"✓ 钥匙扣翻译完成: {translated_count}/{total_count} 项已翻译", log_file)
        return True
        
    except Exception as e:
        log_message(f"✗ 钥匙扣翻译失败: {str(e)}", log_file)
        return False

def translate_music_kits(log_file):
    """翻译音乐盒数据"""
    input_file = os.path.join(INPUT_DIR, "music.json")
    output_file = os.path.join(OUTPUT_DIR, "music.json")
    
    if not os.path.exists(input_file):
        log_message(f"错误: 找不到音乐盒输入文件 {input_file}", log_file)
        return False
    
    log_message("开始翻译音乐盒数据...", log_file)
    
    # 初始化音乐盒翻译器
    translator = MusicKitTranslator()
    if not translator.load_translations():
        log_message("音乐盒翻译器初始化失败", log_file)
        return False
    
    translator.build_index()
    
    # 读取输入文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            log_message(f"错误: 音乐盒文件格式不正确，应为JSON数组", log_file)
            return False
        
        # 翻译
        translated_count = 0
        total_count = len(data)
        
        for i, item in enumerate(data):
            original_name = item.get('name', '')
            translated_item = translator.translate_item(item)
            
            # 检查是否翻译成功
            if translated_item.get('name', '') != original_name:
                translated_count += 1
            
            # 更新原始数据
            data[i] = translated_item
        
        # 保存结果
        save_translated_data(data, output_file)
        
        log_message(f"✓ 音乐盒翻译完成: {translated_count}/{total_count} 项已翻译", log_file)
        return True
        
    except Exception as e:
        log_message(f"✗ 音乐盒翻译失败: {str(e)}", log_file)
        return False

def translate_skins_gloves(log_file):
    """翻译皮肤和手套数据"""
    skin_input_file = os.path.join(INPUT_DIR, "skins.json")
    skin_output_file = os.path.join(OUTPUT_DIR, "skins.json")
    
    glove_input_file = os.path.join(INPUT_DIR, "gloves.json")
    glove_output_file = os.path.join(OUTPUT_DIR, "gloves.json")
    
    if not os.path.exists(skin_input_file) and not os.path.exists(glove_input_file):
        log_message(f"错误: 找不到皮肤/手套输入文件", log_file)
        return False
    
    log_message("开始翻译皮肤和手套数据...", log_file)
    
    # 初始化皮肤/手套翻译器
    translator = SkinGloveTranslator()
    if not translator.load_translations():
        log_message("皮肤/手套翻译器初始化失败", log_file)
        return False
    
    translator.build_index()
    
    # 处理皮肤文件
    success = True
    if os.path.exists(skin_input_file):
        try:
            log_message("处理皮肤数据...", log_file)
            with open(skin_input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                log_message(f"错误: 皮肤文件格式不正确，应为JSON数组", log_file)
                success = False
            else:
                # 翻译
                translated_count = 0
                total_count = len(data)
                
                for i, item in enumerate(data):
                    original_name = item.get('paint_name', '')
                    translated_item = translator.translate_item(item, is_glove=False)
                    
                    # 检查是否翻译成功
                    if translated_item.get('paint_name', '') != original_name:
                        translated_count += 1
                    
                    # 更新原始数据
                    data[i] = translated_item
                
                # 保存结果
                save_translated_data(data, skin_output_file)
                
                log_message(f"✓ 皮肤翻译完成: {translated_count}/{total_count} 项已翻译", log_file)
        except Exception as e:
            log_message(f"✗ 皮肤翻译失败: {str(e)}", log_file)
            success = False
    
    # 处理手套文件
    if os.path.exists(glove_input_file):
        try:
            log_message("处理手套数据...", log_file)
            with open(glove_input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                log_message(f"错误: 手套文件格式不正确，应为JSON数组", log_file)
                success = False
            else:
                # 翻译
                translated_count = 0
                total_count = len(data)
                
                for i, item in enumerate(data):
                    original_name = item.get('paint_name', '')
                    translated_item = translator.translate_item(item, is_glove=True)
                    
                    # 检查是否翻译成功
                    if translated_item.get('paint_name', '') != original_name:
                        translated_count += 1
                    
                    # 更新原始数据
                    data[i] = translated_item
                
                # 保存结果
                save_translated_data(data, glove_output_file)
                
                log_message(f"✓ 手套翻译完成: {translated_count}/{total_count} 项已翻译", log_file)
        except Exception as e:
            log_message(f"✗ 手套翻译失败: {str(e)}", log_file)
            success = False
    
    return success

def translate_stickers(log_file):
    """翻译印花数据"""
    input_file = os.path.join(INPUT_DIR, "stickers.json")
    output_file = os.path.join(OUTPUT_DIR, "stickers.json")
    
    if not os.path.exists(input_file):
        log_message(f"错误: 找不到印花输入文件 {input_file}", log_file)
        return False
    
    log_message("开始翻译印花数据...", log_file)
    
    # 初始化印花翻译器
    translator = StickerTranslator()
    if not translator.load_translations():
        log_message("印花翻译器初始化失败", log_file)
        return False
    
    translator.build_index()
    
    # 读取输入文件
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            log_message(f"错误: 印花文件格式不正确，应为JSON数组", log_file)
            return False
        
        # 翻译
        translated_count = 0
        total_count = len(data)
        
        for i, item in enumerate(data):
            original_name = item.get('name', '')
            translated_item = translator.translate_item(item)
            
            # 检查是否翻译成功
            if translated_item.get('name', '') != original_name:
                translated_count += 1
            
            # 更新原始数据
            data[i] = translated_item
        
        # 保存结果
        save_translated_data(data, output_file)
        
        log_message(f"✓ 印花翻译完成: {translated_count}/{total_count} 项已翻译", log_file)
        return True
        
    except Exception as e:
        log_message(f"✗ 印花翻译失败: {str(e)}", log_file)
        return False

def main():
    start_time = time.time()
    log_file = get_log_file()
    
    # 显示欢迎信息
    log_message("=" * 60, log_file)
    log_message("CS2 物品翻译工具 v1.0", log_file)
    log_message("=" * 60, log_file)
    
    # 顺序执行各个翻译任务
    results = {
        "探员": translate_agents(log_file),
        "钥匙扣": translate_keychains(log_file),
        "音乐盒": translate_music_kits(log_file),
        "皮肤/手套": translate_skins_gloves(log_file),
        "印花": translate_stickers(log_file)
    }
    
    # 显示总结报告
    log_message("\n" + "=" * 60, log_file)
    log_message("翻译任务总结:", log_file)
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    for category, result in results.items():
        status = "✓ 成功" if result else "✗ 失败"
        log_message(f"{category}: {status}", log_file)
    
    elapsed_time = time.time() - start_time
    log_message(f"\n总计: {success_count}/{total_count} 个任务成功", log_file)
    log_message(f"总耗时: {elapsed_time:.2f} 秒", log_file)
    log_message("=" * 60, log_file)
    
    return 0 if success_count == total_count else 1

if __name__ == "__main__":
    sys.exit(main())