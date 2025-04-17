import json
import os
import requests
from urllib.parse import urljoin
from collections import defaultdict

# 配置部分
BASE_API_URL = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/zh-CN/"
CACHE_DIR = "translation_cache"
OUTPUT_DIR = "translated"
os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

class AgentTranslator:
    def __init__(self):
        self.translations = {}
        self.index = defaultdict(dict)
    
    def load_translations(self):
        """加载探员翻译数据"""
        cache_file = os.path.join(CACHE_DIR, "agents.json")
        api_url = urljoin(BASE_API_URL, "agents.json")
        
        try:
            # 尝试从缓存加载
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.translations = json.load(f)
                print("✓ 从缓存加载探员翻译数据")
                return True
            
            # 从API下载
            print("正在下载探员翻译数据...")
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            self.translations = response.json()
            
            # 保存到缓存
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.translations, f, ensure_ascii=False, indent=2)
            
            print("✓ 探员翻译数据下载成功")
            return True
        except Exception as e:
            print(f"✗ 加载探员翻译数据失败: {str(e)}")
            return False
    
    def build_index(self):
        """构建探员翻译索引"""
        if not self.translations:
            return False
        
        for agent in self.translations:
            # 通过model_player路径匹配
            if model := agent.get('model_player'):
                # 标准化路径格式 (兼容不同斜杠方向)
                normalized_model = model.replace('\\', '/').lower()
                self.index['model'][normalized_model] = agent
            
            # 通过market_hash_name匹配
            if market_name := agent.get('market_hash_name'):
                self.index['market_name'][market_name.lower()] = agent
            
            # 通过名称匹配
            if name := agent.get('name'):
                self.index['name'][name.lower()] = agent
        
        print(f"✓ 已建立 {len(self.translations)} 条探员翻译索引")
        return True
    
    def translate_item(self, item):
        """翻译单个探员项目"""
        # 检查是否已经是中文
        if self._is_already_translated(item.get('agent_name', '')):
            return item
        
        translation = None
        
        # 1. 通过model路径匹配
        if 'model' in item:
            # 标准化模型路径
            normalized_model = item['model'].replace('\\', '/').lower()
            translation = self.index['model'].get(normalized_model)
        
        # 2. 通过agent_name匹配
        if not translation and 'agent_name' in item:
            # 尝试完整匹配
            translation = self.index['market_name'].get(item['agent_name'].lower())
            # 尝试去除代号部分匹配 (如 "'Blueberries' Buckshot" → "Buckshot")
            if not translation and "'" in item['agent_name']:
                clean_name = item['agent_name'].split('|')[0].split("'")[-1].strip()
                translation = self.index['market_name'].get(clean_name.lower())
        
        if translation:
            # 应用翻译
            item['agent_name'] = translation['name']
            return item
        
        return item
    
    def _is_already_translated(self, text):
        """检查文本是否已包含中文字符"""
        if not text:
            return False
        return any('\u4e00' <= char <= '\u9fff' for char in text)
    
    def translate_file(self, input_file):
        """翻译整个探员文件"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print("错误: 输入文件格式不正确，应为探员数组")
                return False
            
            total = len(data)
            translated = 0
            
            for i, item in enumerate(data, 1):
                original_name = item.get('agent_name', '')
                result = self.translate_item(item)
                
                if result.get('agent_name', '') != original_name:
                    translated += 1
                
                # 进度显示
                if i % 10 == 0 or i == total:
                    print(f"\r处理进度: {i}/{total} ({translated} 已翻译)", end='')
            
            # 保存结果
            output_file = os.path.join(OUTPUT_DIR, os.path.basename(input_file))
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ 翻译完成! 结果已保存到 {output_file}")
            print(f"统计: 共 {total} 条，{translated} 条已翻译")
            return True
        except Exception as e:
            print(f"\n✗ 翻译文件时出错: {str(e)}")
            return False

def main():
    print("=== CSGO探员专用翻译工具 ===")
    print("正在初始化...\n")
    
    translator = AgentTranslator()
    
    # 1. 加载翻译数据
    if not translator.load_translations():
        print("无法继续，请检查网络连接或API可用性")
        return
    
    # 2. 构建索引
    if not translator.build_index():
        print("无法构建翻译索引")
        return
    
    # 3. 处理文件
    input_file = "agents.json"
    if not os.path.exists(input_file):
        print(f"错误: 输入文件 {input_file} 不存在")
        return
    
    print(f"\n开始翻译文件: {input_file}")
    translator.translate_file(input_file)

if __name__ == '__main__':
    main()