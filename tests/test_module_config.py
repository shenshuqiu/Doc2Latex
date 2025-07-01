#!/usr/bin/env python3
"""
模块配置功能测试脚本

测试新添加的可配置模块颜色系统的各项功能
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path

def test_basic_config_loading():
    """测试基本配置加载功能"""
    print("=" * 50)
    print("测试1: 基本配置加载功能")
    print("=" * 50)
    
    try:
        # 清理已导入的模块以重新加载
        if 'doc2latex.config.settings' in sys.modules:
            del sys.modules['doc2latex.config.settings']
            
        from doc2latex.config.settings import BOX_DICT, BOX_DICT_TRADITIONAL
        
        print("✅ 成功加载配置")
        print("简体中文模块配置:")
        for module, color in BOX_DICT.items():
            print(f"  {module}: {color}")
        
        print("\n繁体中文模块配置:")
        for module, color in BOX_DICT_TRADITIONAL.items():
            print(f"  {module}: {color}")
            
        # 验证配置是否正确
        expected_modules = ["名词解释", "操作步骤", "实用建议", "编者的话", "就医建议"]
        expected_colors = ["green", "orange", "red"]
        
        assert all(module in BOX_DICT for module in expected_modules), "缺少必要的模块"
        assert all(color in expected_colors for color in BOX_DICT.values()), "包含未知颜色"
        
        print("\n✅ 配置验证通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_config_file_error_handling():
    """测试配置文件错误处理"""
    print("\n" + "=" * 50)
    print("测试2: 配置文件错误处理")
    print("=" * 50)
    
    config_path = Path("doc2latex/config/modules.json")
    backup_path = Path("doc2latex/config/modules.json.backup")
    
    try:
        # 备份原配置文件
        if config_path.exists():
            shutil.copy(config_path, backup_path)
            
        # 测试1: 配置文件不存在
        print("测试配置文件不存在的情况...")
        if config_path.exists():
            config_path.unlink()
            
        # 清理模块缓存并重新导入
        if 'doc2latex.config.settings' in sys.modules:
            del sys.modules['doc2latex.config.settings']
            
        from doc2latex.config.settings import BOX_DICT
        print("✅ 配置文件不存在时使用默认配置成功")
        
        # 测试2: 配置文件格式错误
        print("\n测试配置文件格式错误的情况...")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
            
        # 清理模块缓存并重新导入
        if 'doc2latex.config.settings' in sys.modules:
            del sys.modules['doc2latex.config.settings']
            
        from doc2latex.config.settings import BOX_DICT
        print("✅ 配置文件格式错误时使用默认配置成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
        
    finally:
        # 恢复原配置文件
        if backup_path.exists():
            shutil.move(backup_path, config_path)

def test_dynamic_config_update():
    """测试动态配置更新"""
    print("\n" + "=" * 50)
    print("测试3: 动态配置更新")
    print("=" * 50)
    
    config_path = Path("doc2latex/config/modules.json")
    backup_path = Path("doc2latex/config/modules.json.backup")
    
    try:
        # 备份原配置
        if config_path.exists():
            shutil.copy(config_path, backup_path)
            
        # 创建测试配置
        test_config = {
            "description": "测试配置",
            "version": "1.0",
            "available_colors": ["green", "orange", "red"],
            "modules": {
                "测试模块1": "green",
                "测试模块2": "orange",
                "实用建议": "red"
            },
            "modules_traditional": {
                "測試模組1": "green",
                "測試模組2": "orange", 
                "實用建議": "red"
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(test_config, f, ensure_ascii=False, indent=2)
            
        # 清理模块缓存并重新导入
        if 'doc2latex.config.settings' in sys.modules:
            del sys.modules['doc2latex.config.settings']
            
        from doc2latex.config.settings import BOX_DICT, BOX_DICT_TRADITIONAL
        
        print("更新后的配置:")
        for module, color in BOX_DICT.items():
            print(f"  {module}: {color}")
            
        # 验证配置是否更新
        assert "测试模块1" in BOX_DICT, "新模块未加载"
        assert BOX_DICT["测试模块1"] == "green", "模块颜色不正确"
        assert BOX_DICT["实用建议"] == "red", "颜色更新失败"
        
        print("✅ 动态配置更新成功")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
        
    finally:
        # 恢复原配置
        if backup_path.exists():
            shutil.move(backup_path, config_path)

def test_traditional_chinese_config():
    """测试繁体中文配置"""
    print("\n" + "=" * 50)
    print("测试4: 繁体中文配置")
    print("=" * 50)
    
    try:
        # 清理模块缓存
        if 'doc2latex.config.settings' in sys.modules:
            del sys.modules['doc2latex.config.settings']
            
        from doc2latex.config.settings import BOX_DICT_TRADITIONAL
        
        print("繁体中文模块配置:")
        for module, color in BOX_DICT_TRADITIONAL.items():
            print(f"  {module}: {color}")
            
        # 验证繁体配置
        expected_traditional = ["名詞解釋", "操作步驟", "實用建議", "編者的話", "就醫建議"]
        assert all(module in BOX_DICT_TRADITIONAL for module in expected_traditional), "缺少繁体模块"
        
        print("✅ 繁体中文配置测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_color_validation():
    """测试颜色验证"""
    print("\n" + "=" * 50)
    print("测试5: 颜色验证")
    print("=" * 50)
    
    try:
        from doc2latex.config.settings import BOX_DICT
        
        # 检查所有颜色都是预定义的颜色
        valid_colors = {"green", "orange", "red"}
        used_colors = set(BOX_DICT.values())
        
        print(f"使用的颜色: {used_colors}")
        print(f"有效颜色: {valid_colors}")
        
        invalid_colors = used_colors - valid_colors
        if invalid_colors:
            print(f"❌ 发现无效颜色: {invalid_colors}")
            return False
        else:
            print("✅ 所有颜色都有效")
            return True
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始模块配置功能测试")
    print("=" * 60)
    
    tests = [
        test_basic_config_loading,
        test_config_file_error_handling, 
        test_dynamic_config_update,
        test_traditional_chinese_config,
        test_color_validation
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
        
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过!")
        return True
    else:
        print("❌ 部分测试失败")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)