import json
import os
import requests
from urllib.parse import urljoin
from collections import defaultdict

class SkinGloveTranslator:
    def __init__(self):
        self.translations = []
        self.index = defaultdict(dict)
        self.debug = False  # 禁用调试模式，避免刷屏
        
    def load_translations(self):
        """加载皮肤和手套翻译数据"""
        api_url = "https://raw.githubusercontent.com/ByMykel/CSGO-API/main/public/api/zh-CN/skins.json"
        try:
            response = requests.get(api_url, timeout=30)
            response.raise_for_status()
            self.translations = response.json()
            print(f"✓ 已加载 {len(self.translations)} 条皮肤/手套翻译数据")
            return True
        except Exception as e:
            print(f"✗ 加载失败: {str(e)}")
            return False
    
    def build_index(self):
        """构建翻译索引"""
        if not self.translations:
            return False
            
        for item in self.translations:
            if not isinstance(item, dict):
                continue
                
            # 安全获取嵌套字段
            weapon_data = item.get('weapon', {}) or {}
            pattern_data = item.get('pattern', {}) or {}
            category_data = item.get('category', {}) or {}
            
            weapon_id = weapon_data.get('weapon_id')
            paint_index = item.get('paint_index')
            
            # 只处理有效条目
            if not all([weapon_data, weapon_id is not None, paint_index is not None]):
                continue
                
            # 通过武器ID和涂装ID索引
            key = f"{weapon_id}_{paint_index}"
            self.index['weapon_paint'][key] = item
            
            # 通过皮肤名称索引
            weapon_name = weapon_data.get('name', '')
            pattern_name = pattern_data.get('name', '')
            
            if weapon_name and pattern_name:
                # 标准格式
                full_name = f"{weapon_name} | {pattern_name}"
                self.index['full_name'][full_name.lower()] = item
                
                # 为手套添加特殊处理
                if category_data.get('id') == 'sfui_invpanel_filter_gloves':
                    # 带★的格式
                    starred_name = f"★ {weapon_name} | {pattern_name}"
                    self.index['full_name'][starred_name.lower()] = item
                    
                    # 反向映射
                    cn_name = item.get('name', '')
                    if cn_name and '|' in cn_name:
                        en_name = self._reverse_map_name(cn_name)
                        if en_name:
                            self.index['reverse_name'][en_name.lower()] = item
        
        print(f"✓ 已建立索引 (武器涂装: {len(self.index['weapon_paint'])}, 完整名称: {len(self.index['full_name'])})")
        return True
    
    def _reverse_map_name(self, cn_name):
        """从中文名反向映射英文名"""
        # 更完整的手套映射
        name_map = {
            '狂牙手套': 'Broken Fang Gloves',
            '翡翠': 'Jade',
            '运动手套': 'Sport Gloves',
            '摩托手套': 'Moto Gloves',
            '专业手套': 'Specialist Gloves',
            '驾驶手套': 'Driver Gloves',
            '血猎手套': 'Bloodhound Gloves',
            '九头蛇手套': 'Hydra Gloves',
        }
        
        parts = [p.strip() for p in cn_name.split('|', 1)]
        if len(parts) != 2:
            return None
            
        weapon_part = parts[0].replace('（★）', '').replace('(★)', '').strip()
        pattern_part = parts[1].strip()
        
        en_weapon = name_map.get(weapon_part, weapon_part)
        en_pattern = name_map.get(pattern_part, pattern_part)
        
        return f"{en_weapon} | {en_pattern}"
    
    def translate_item(self, item, is_glove=False):
        """翻译单个项目"""
        if not isinstance(item, dict):
            return item
            
        original_name = item.get('paint_name', '')
        if not original_name:
            return item
            
        # 1. 通过武器ID和涂装ID匹配
        weapon_id = item.get('weapon_defindex')
        paint_id = item.get('paint')
        if weapon_id is not None and paint_id is not None:
            key = f"{weapon_id}_{paint_id}"
            if translation := self.index['weapon_paint'].get(key):
                return self._apply_translation(item, translation, original_name)
        
        # 2. 通过名称匹配
        # 尝试直接匹配
        if translation := self.index['full_name'].get(original_name.lower()):
            return self._apply_translation(item, translation, original_name)
        
        # 尝试去除★前缀
        if original_name.startswith('★ '):
            clean_name = original_name[2:]
            if translation := self.index['full_name'].get(clean_name.lower()):
                return self._apply_translation(item, translation, original_name)
        
        # 3. 反向映射匹配 (主要用于手套)
        if is_glove:
            if translation := self.index['reverse_name'].get(original_name.lower()):
                return self._apply_translation(item, translation, original_name)
        
        return item
    
    def _apply_translation(self, item, translation, original_name):
        """应用翻译结果"""
        translated_name = translation.get('name', '')
        if not translated_name or translated_name == original_name:
            return item
            
        # 保留原始★标记
        if original_name.startswith('★ ') and not translated_name.startswith('★'):
            if '（★）' not in translated_name and '(★)' not in translated_name:
                translated_name = translated_name.replace('手套', '手套（★）', 1)
        
        item['paint_name'] = translated_name
        return item
    
    def translate_file(self, input_file, is_glove=False):
        """翻译整个文件"""
        try:
            print(f"\n开始处理文件: {input_file}")
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print("错误: 输入文件格式不正确，应为JSON数组")
                return False
                
            total = len(data)
            translated = 0
            
            for i, item in enumerate(data, 1):
                if not isinstance(item, dict):
                    continue
                    
                original_name = item.get('paint_name', '')
                result = self.translate_item(item, is_glove)
                if result.get('paint_name', '') != original_name:
                    translated += 1
                
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
            print(f"\n✗ 处理文件时出错: {str(e)}")
            return False

def main():
    print("=== CS手套/皮肤翻译工具 ===")
    translator = SkinGloveTranslator()
    
    print("\n步骤1: 加载翻译数据...")
    if not translator.load_translations():
        return
    
    print("\n步骤2: 构建翻译索引...")
    if not translator.build_index():
        return
    
    # 处理手套文件
    glove_file = "gloves.json"
    if os.path.exists(glove_file):
        translator.translate_file(glove_file, is_glove=True)
    else:
        print(f"\n警告: 未找到手套文件 {glove_file}")
    
    # 处理皮肤文件
    skin_file = "skins.json"
    if os.path.exists(skin_file):
        translator.translate_file(skin_file, is_glove=False)
    else:
        print(f"\n警告: 未找到皮肤文件 {skin_file}")

if __name__ == '__main__':
    main()