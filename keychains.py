import json
import os
import requests
from urllib.parse import urljoin
from collections import defaultdict

class KeychainTranslator:
    def __init__(self):
        self.translations = []
        self.index = defaultdict(dict)
        
    def load_translations(self):
        """加载钥匙扣翻译数据"""
        api_url = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/zh-CN/keychains.json"
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            self.translations = response.json()
            print(f"✓ 已加载 {len(self.translations)} 条钥匙扣翻译数据")
            return True
        except Exception as e:
            print(f"✗ 加载失败: {str(e)}")
            return False
    
    def build_index(self):
        """构建钥匙扣翻译索引"""
        if not self.translations:
            return False
            
        for item in self.translations:
            if not isinstance(item, dict):
                continue
                
            # 通过ID索引 (兼容带/不带keychain-前缀)
            item_id = item.get('id', '')
            if item_id:
                base_id = item_id.replace('keychain-', '')
                self.index['id'][base_id] = item
            
            # 通过英文名索引 (去除"Patch | "前缀)
            original_name = item.get('name', '')
            if original_name:
                clean_name = original_name.replace('挂件 | ', '')
                self.index['name'][clean_name.lower()] = item
        
        print(f"✓ 已建立索引 (ID: {len(self.index['id'])}, 名称: {len(self.index['name'])})")
        return True
    
    def translate_item(self, item):
        """翻译单个钥匙扣项目"""
        if not isinstance(item, dict):
            return item
            
        # 1. 通过ID匹配 (兼容两种格式)
        item_id = str(item.get('id', ''))
        if item_id:
            # 尝试直接匹配
            if translation := self.index['id'].get(item_id):
                return self._apply_translation(item, translation)
            
            # 尝试添加keychain-前缀
            prefixed_id = f"keychain-{item_id}"
            if translation := self.index['id'].get(prefixed_id.replace('keychain-', '')):
                return self._apply_translation(item, translation)
        
        # 2. 通过名称匹配
        item_name = item.get('name', '')
        if item_name:
            # 尝试完整匹配
            if translation := self.index['name'].get(item_name.lower()):
                return self._apply_translation(item, translation)
            
            # 尝试去除可能的前缀
            clean_name = item_name.replace('Keychain | ', '').replace('Patch | ', '').strip()
            if translation := self.index['name'].get(clean_name.lower()):
                return self._apply_translation(item, translation)
        
        return item
    
    def _apply_translation(self, item, translation):
        """应用翻译到项目"""
        if not isinstance(translation, dict):
            return item
            
        translated_name = translation.get('name', '')
        if not translated_name:
            return item
            
        # 清洗翻译结果 (去除"挂件 | "前缀)
        if '挂件 | ' in translated_name:
            translated_name = translated_name.split('挂件 | ')[1]
        
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
    print("=== CSGO钥匙扣翻译工具 ===")
    translator = KeychainTranslator()
    
    if not translator.load_translations():
        return
    
    if not translator.build_index():
        return
    
    input_file = "keychains.json"  # 修改为您的输入文件路径
    if not os.path.exists(input_file):
        print(f"错误: 文件 {input_file} 不存在")
        return
    
    print(f"\n开始翻译文件: {input_file}")
    translator.translate_file(input_file)

if __name__ == '__main__':
    main()