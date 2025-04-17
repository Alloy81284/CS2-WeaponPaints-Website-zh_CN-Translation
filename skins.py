import json
import os
import requests
from urllib.parse import urljoin
from collections import defaultdict
import re

class SkinGloveTranslator:
    def __init__(self):
        self.translations = []
        self.index = defaultdict(dict)
        self.weapon_names = {}  # 武器基础名称映射
        self.weapon_codes = {}  # 武器代码到ID的映射
        self.english_to_chinese = {}  # 英文武器名到中文名的映射
        self.debug = False  # 调试模式
        
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
            
        # 基础武器英文名称到中文的映射表
        basic_weapon_map = {
            "Desert Eagle": "沙漠之鹰",
            "Dual Berettas": "双持贝瑞塔",
            "Five-SeveN": "FN57",
            "Glock-18": "格洛克 18 型",
            "AK-47": "AK-47",
            "AWP": "AWP",
            "M4A4": "M4A4",
            "M4A1-S": "M4A1消音版",
            "USP-S": "USP消音版",
            "P2000": "P2000",
            "P250": "P250",
            "R8 Revolver": "R8 左轮手枪",
            "Tec-9": "Tec-9",
            "CZ75-Auto": "CZ75",
            "MP9": "MP9",
            "MP7": "MP7",
            "UMP-45": "UMP-45",
            "P90": "P90",
            "MAC-10": "MAC-10",
            "PP-Bizon": "PP-野牛",
            "Nova": "新星",
            "XM1014": "XM1014",
            "MAG-7": "MAG-7",
            "Sawed-Off": "短管散弹枪",
            "M249": "M249",
            "Negev": "内格夫",
            "FAMAS": "法玛斯",
            "Galil AR": "加利尔 AR",
            "SSG 08": "SSG 08",
            "SG 553": "SG 553",
            "AUG": "AUG",
            "G3SG1": "G3SG1",
            "SCAR-20": "SCAR-20",
            "Bayonet": "刺刀",
            "Gut Knife": "穿肠刀",
            "Karambit": "爪子刀",
            "M9 Bayonet": "M9刺刀",
            "Huntsman Knife": "猎杀者匕首",
            "Flip Knife": "折叠刀",
            "Butterfly Knife": "蝴蝶刀",
            "Falchion Knife": "弯刀",
            "Shadow Daggers": "暗影双匕",
            "Bowie Knife": "鲍伊猎刀",
            "Survival Knife": "求生匕首",
            "Ursus Knife": "熊刀",
            "Navaja Knife": "折刀",
            "Stiletto Knife": "短剑",
            "Talon Knife": "锯齿爪刀",
            "Classic Knife": "海豹短刀",
            "Paracord Knife": "伞绳刀",
            "Survival Knife": "求生刀",
            "Skeleton Knife": "骷髅刀",
            "Nomad Knife": "流浪者匕首",
            "Default Knife": "默认刀具"
        }
        
        # 初始化英文到中文的映射
        self.english_to_chinese.update(basic_weapon_map)
            
        for item in self.translations:
            if not isinstance(item, dict):
                continue
                
            # 安全获取嵌套字段
            weapon_data = item.get('weapon', {}) or {}
            pattern_data = item.get('pattern', {}) or {}
            category_data = item.get('category', {}) or {}
            
            weapon_id = weapon_data.get('weapon_id')
            weapon_name = weapon_data.get('name', '')
            weapon_code = weapon_data.get('id', '')
            paint_index = item.get('paint_index')
            
            # 存储武器基础名称映射
            if weapon_id is not None and weapon_name:
                self.weapon_names[weapon_id] = weapon_name
                
                # 存储武器代码到ID的映射
                if weapon_code:
                    self.weapon_codes[weapon_code] = weapon_id
                    
                # 尝试从名称中提取英文武器名
                en_name = ""
                for en, zh in basic_weapon_map.items():
                    if zh == weapon_name:
                        en_name = en
                        break
                
                if en_name:
                    self.english_to_chinese[en_name] = weapon_name
            
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
                
                # 为手套和刀具添加特殊处理
                if category_data.get('id') in ['sfui_invpanel_filter_gloves', 'knife']:
                    # 带★的格式
                    starred_name = f"★ {weapon_name} | {pattern_name}"
                    self.index['full_name'][starred_name.lower()] = item
                    
                    # 反向映射
                    cn_name = item.get('name', '')
                    if cn_name and '|' in cn_name:
                        en_name = self._reverse_map_name(cn_name)
                        if en_name:
                            self.index['reverse_name'][en_name.lower()] = item
        
        print(f"✓ 已建立索引 (武器涂装: {len(self.index['weapon_paint'])}, 完整名称: {len(self.index['full_name'])}, 武器基础名称: {len(self.weapon_names)})")
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
        
        # 2. 处理Default默认皮肤
        if ' | Default' in original_name:
            # 解析原始武器名称
            parts = original_name.split(' | ')[0].strip()
            has_star = parts.startswith('★ ')
            weapon_en_name = parts[2:] if has_star else parts
            
            # 方法1: 从预定义映射表查找
            if weapon_zh_name := self.english_to_chinese.get(weapon_en_name):
                new_item = item.copy()
                if has_star:
                    new_item['paint_name'] = f"{weapon_zh_name}（★）"
                else:
                    new_item['paint_name'] = weapon_zh_name
                return new_item
            
            # 方法2: 通过武器ID查找
            if weapon_id is not None and (weapon_zh_name := self.weapon_names.get(weapon_id)):
                new_item = item.copy()
                if has_star:
                    new_item['paint_name'] = f"{weapon_zh_name}（★）"
                else:
                    new_item['paint_name'] = weapon_zh_name
                return new_item
            
            # 方法3: 通过武器代码查找
            weapon_code = item.get('weapon_name', '')
            if weapon_code and weapon_code.startswith('weapon_'):
                base_code = weapon_code.replace('weapon_', '')
                
                # 先查找完整匹配
                for code, w_id in self.weapon_codes.items():
                    if base_code == code.replace('weapon_', ''):
                        if weapon_zh_name := self.weapon_names.get(w_id):
                            new_item = item.copy()
                            if has_star:
                                new_item['paint_name'] = f"{weapon_zh_name}（★）"
                            else:
                                new_item['paint_name'] = weapon_zh_name
                            return new_item
                
                # 再查找部分匹配
                for code, w_id in self.weapon_codes.items():
                    if base_code in code:
                        if weapon_zh_name := self.weapon_names.get(w_id):
                            new_item = item.copy()
                            if has_star:
                                new_item['paint_name'] = f"{weapon_zh_name}（★）"
                            else:
                                new_item['paint_name'] = weapon_zh_name
                            return new_item
        
        # 3. 通过名称匹配
        # 尝试直接匹配
        if translation := self.index['full_name'].get(original_name.lower()):
            return self._apply_translation(item, translation, original_name)
        
        # 尝试去除★前缀
        if original_name.startswith('★ '):
            clean_name = original_name[2:]
            if translation := self.index['full_name'].get(clean_name.lower()):
                return self._apply_translation(item, translation, original_name)
        
        # 4. 反向映射匹配 (主要用于手套)
        if is_glove:
            if translation := self.index['reverse_name'].get(original_name.lower()):
                return self._apply_translation(item, translation, original_name)
        
        # 5. 尝试直接根据英文名称翻译(兜底处理)
        parts = original_name.split(' | ')
        if len(parts) == 2 and parts[1] == 'Default':
            has_star = parts[0].startswith('★ ')
            weapon_name = parts[0][2:] if has_star else parts[0]
            
            if zh_name := self.english_to_chinese.get(weapon_name):
                new_item = item.copy()
                if has_star:
                    new_item['paint_name'] = f"{zh_name}（★）"
                else:
                    new_item['paint_name'] = zh_name
                return new_item
        
        return item
    
    def _apply_translation(self, item, translation, original_name):
        """应用翻译结果"""
        translated_name = translation.get('name', '')
        if not translated_name or translated_name == original_name:
            return item
            
        # 保留原始★标记
        if original_name.startswith('★ ') and not translated_name.startswith('★'):
            if '（★）' not in translated_name and '(★)' not in translated_name:
                if '手套' in translated_name:
                    translated_name = translated_name.replace('手套', '手套（★）', 1)
                else:
                    translated_name = f"{translated_name}（★）"
        
        new_item = item.copy()
        new_item['paint_name'] = translated_name
        return new_item
    
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
            untranslated = []
            
            for i, item in enumerate(data, 1):
                if not isinstance(item, dict):
                    continue
                    
                original_name = item.get('paint_name', '')
                result = self.translate_item(item, is_glove)
                
                # 检查是否成功翻译
                if result.get('paint_name', '') != original_name:
                    translated += 1
                    if self.debug:
                        print(f"\n翻译: {original_name} -> {result.get('paint_name', '')}")
                    # 更新原始数据
                    data[i-1] = result
                else:
                    untranslated.append(original_name)
                
                if i % 100 == 0 or i == total:
                    print(f"\r进度: {i}/{total} ({translated} 已翻译)", end='')
            
            # 保存结果
            os.makedirs('translated', exist_ok=True)
            output_file = os.path.join('translated', os.path.basename(input_file))
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ 翻译完成! {translated}/{total} 条已翻译")
            print(f"结果已保存到: {output_file}")
            
            # 输出未翻译的条目
            if untranslated and len(untranslated) < 20:
                print("\n未翻译的条目:")
                for name in untranslated:
                    print(f"- {name}")
            
            return True
            
        except Exception as e:
            print(f"\n✗ 处理文件时出错: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return False

def main():
    print("=== CS手套/皮肤翻译工具 v1.1 ===")
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
