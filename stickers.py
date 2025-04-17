import json
import os
import requests
from urllib.parse import urljoin
from collections import defaultdict

class StickerTranslator:
    def __init__(self):
        self.translations = []
        self.index = defaultdict(dict)
        
    def load_translations(self):
        """加载印花翻译数据"""
        api_url = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/zh-CN/stickers.json"
        try:
            response = requests.get(api_url, timeout=15)  # 增加超时时间
            response.raise_for_status()
            self.translations = response.json()
            print(f"✓ 已加载 {len(self.translations)} 条印花翻译数据")
            return True
        except Exception as e:
            print(f"✗ 加载失败: {str(e)}")
            return False
    
    def build_index(self):
        """构建印花翻译索引"""
        if not self.translations:
            return False
            
        for item in self.translations:
            if not isinstance(item, dict):
                continue
                
            # 通过ID索引 (兼容带/不带sticker-前缀)
            item_id = item.get('id', '')
            if item_id:
                base_id = item_id.replace('sticker-', '')
                self.index['id'][base_id] = item
            
            # 通过英文名索引 (去除"Sticker | "前缀)
            original_name = item.get('name', '')
            if original_name:
                # 去除中文前缀
                clean_name = original_name.replace('印花 | ', '')
                # 去除可能存在的HTML标签
                clean_name = clean_name.split('<')[0].strip()
                self.index['name'][clean_name.lower()] = item
                
                # 添加原始名称索引
                self.index['original_name'][original_name.lower()] = item
        
        print(f"✓ 已建立索引 (ID: {len(self.index['id'])}, 名称: {len(self.index['name'])})")
        return True
    
    def translate_item(self, item):
        """翻译单个印花项目"""
        if not isinstance(item, dict):
            return item
            
        # 1. 通过ID匹配 (兼容两种格式)
        item_id = str(item.get('id', ''))
        if item_id:
            # 尝试直接匹配
            if translation := self.index['id'].get(item_id):
                return self._apply_translation(item, translation)
            
            # 尝试添加sticker-前缀
            prefixed_id = f"sticker-{item_id}"
            if translation := self.index['id'].get(prefixed_id.replace('sticker-', '')):
                return self._apply_translation(item, translation)
        
        # 2. 通过名称匹配
        item_name = item.get('name', '')
        if item_name:
            # 尝试完整匹配
            if translation := self.index['original_name'].get(item_name.lower()):
                return self._apply_translation(item, translation)
            
            # 尝试去除英文前缀
            clean_name = item_name.replace('Sticker | ', '').strip()
            if translation := self.index['name'].get(clean_name.lower()):
                return self._apply_translation(item, translation)
            
            # 尝试最简匹配 (去除所有修饰词)
            simplest_name = clean_name.split('(')[0].split('|')[0].strip()
            if translation := self.index['name'].get(simplest_name.lower()):
                return self._apply_translation(item, translation)
        
        return item
    
    def _apply_translation(self, item, translation):
        """应用翻译到项目"""
        if not isinstance(translation, dict):
            return item
            
        translated_name = translation.get('name', '')
        if not translated_name:
            return item
            
        # 清洗翻译结果 (去除"印花 | "前缀和HTML标签)
        if '印花 | ' in translated_name:
            translated_name = translated_name.split('印花 | ')[1]
        translated_name = translated_name.split('<')[0].strip()
        
        item['name'] = translated_name
        return item
    
    def translate_file(self, input_file):
        """翻译整个文件"""
        try:
            print(f"开始加载输入文件: {input_file}")
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print("错误: 输入文件格式不正确，应为JSON数组")
                return False
                
            total = len(data)
            translated = 0
            
            print("开始翻译...")
            for i, item in enumerate(data, 1):
                if not isinstance(item, dict):
                    continue
                    
                original_name = item.get('name', '')
                translated_item = self.translate_item(item)
                if translated_item.get('name', '') != original_name:
                    translated += 1
                
                # 每100条显示一次进度
                if i % 100 == 0 or i == total:
                    print(f"\r进度: {i}/{total} ({translated} 已翻译)", end='')
            
            # 保存结果
            os.makedirs('translated', exist_ok=True)
            output_file = os.path.join('translated', os.path.basename(input_file))
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ 翻译完成! {translated}/{total} 条已翻译")
            print(f"结果已保存到: {output_file}")
            return True
            
        except Exception as e:
            print(f"\n✗ 文件处理错误: {str(e)}")
            return False

def main():
    print("=== CSGO印花翻译工具 ===")
    translator = StickerTranslator()
    
    print("\n步骤1: 加载翻译数据...")
    if not translator.load_translations():
        return
    
    print("\n步骤2: 构建翻译索引...")
    if not translator.build_index():
        return
    
    input_file = "stickers.json"  # 修改为您的输入文件路径
    if not os.path.exists(input_file):
        print(f"\n错误: 文件 {input_file} 不存在")
        return
    
    print(f"\n步骤3: 开始翻译文件: {input_file}")
    translator.translate_file(input_file)

if __name__ == '__main__':
    main()