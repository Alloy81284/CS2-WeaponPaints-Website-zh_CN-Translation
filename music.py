import json
import os
import requests
from urllib.parse import urljoin
from collections import defaultdict

class MusicKitTranslator:
    def __init__(self):
        self.translations = []
        self.index = defaultdict(dict)
        
    def load_translations(self):
        """加载音乐盒翻译数据"""
        api_url = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/zh-CN/music_kits.json"
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            self.translations = response.json()
            print(f"✓ 已加载 {len(self.translations)} 条音乐盒翻译数据")
            return True
        except Exception as e:
            print(f"✗ 加载失败: {str(e)}")
            return False
    
    def build_index(self):
        """构建音乐盒翻译索引"""
        if not self.translations:
            return False
            
        for item in self.translations:
            if not isinstance(item, dict):
                continue
                
            # 标准化ID (去除_st后缀)
            item_id = item.get('id', '')
            if item_id:
                base_id = item_id.replace('_st', '')
                self.index['id'][base_id] = item
            
            # 通过market_hash_name索引 (安全处理None值)
            market_name = item.get('market_hash_name')
            if market_name:
                clean_name = market_name.replace('StatTrak™ ', '')
                self.index['name'][clean_name.lower()] = item
            
            # 通过显示名称索引
            display_name = item.get('name', '')
            if display_name:
                clean_display = display_name.replace('音乐盒 | ', '').replace('StatTrak™ ', '')
                self.index['display_name'][clean_display.lower()] = item
        
        print(f"✓ 已建立索引 (ID: {len(self.index['id'])}, 名称: {len(self.index['name'])}, 显示名: {len(self.index['display_name'])})")
        return True
    
    def translate_item(self, item):
        """翻译单个音乐盒项目"""
        if not isinstance(item, dict):
            return item
            
        # 1. 通过ID匹配 (兼容带/不带music_kit-前缀)
        item_id = str(item.get('id', ''))
        if item_id:
            search_ids = [
                f"music_kit-{item_id}",
                item_id,
                item_id.replace('music_kit-', '')
            ]
            
            for search_id in search_ids:
                if translation := self.index['id'].get(search_id):
                    return self._apply_translation(item, translation)
        
        # 2. 通过名称匹配
        item_name = item.get('name', '')
        if item_name:
            # 尝试完整匹配
            if translation := self.index['name'].get(item_name.lower()):
                return self._apply_translation(item, translation)
            
            # 尝试去除"Music Kit | "前缀
            clean_name = item_name.replace('Music Kit | ', '')
            if translation := self.index['name'].get(clean_name.lower()):
                return self._apply_translation(item, translation)
            
            # 尝试通过艺术家匹配
            artist_part = item_name.split(',')[0].strip()
            if translation := self.index['display_name'].get(artist_part.lower()):
                return self._apply_translation(item, translation)
        
        return item
    
    def _apply_translation(self, item, translation):
        """应用翻译到项目"""
        if not isinstance(translation, dict):
            return item
            
        translated_name = translation.get('name', '')
        if not translated_name:
            return item
            
        # 清洗翻译结果
        if '音乐盒 | ' in translated_name:
            translated_name = translated_name.split('音乐盒 | ')[1]
        if 'StatTrak™ ' in translated_name and '_st' not in item.get('id', ''):
            translated_name = translated_name.replace('StatTrak™ ', '')
        
        item['name'] = translated_name
        return item
    
    def translate_file(self, input_file):
        """翻译整个文件"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print("错误: 输入文件格式不正确，应为JSON数组")
                return False
                
            total = len(data)
            translated = 0
            
            for item in data:
                if not isinstance(item, dict):
                    continue
                    
                original_name = item.get('name', '')
                translated_item = self.translate_item(item)
                if translated_item.get('name', '') != original_name:
                    translated += 1
            
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
    print("=== CSGO音乐盒精准翻译工具 v2 ===")
    translator = MusicKitTranslator()
    
    if not translator.load_translations():
        return
    
    if not translator.build_index():
        return
    
    input_file = "music.json"  # 修改为您的输入文件路径
    if not os.path.exists(input_file):
        print(f"错误: 文件 {input_file} 不存在")
        return
    
    print(f"\n开始翻译文件: {input_file}")
    translator.translate_file(input_file)

if __name__ == '__main__':
    main()