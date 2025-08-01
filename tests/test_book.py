import sys
import asyncio
import os
import time

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from module.database.book import *


async def test_new_book():
    """测试创建新书籍"""
    print("=" * 50)
    print("测试阶段：创建新书籍")
    print("=" * 50)
    
    # 测试正常创建 - 空书籍
    print("\n🔹 测试创建空书籍")
    empty_book = Book(
        id="",  # ID将被自动生成
        title="测试空书籍",
        chapters=[]
    )
    
    result = await new_book(empty_book)
    print(f"✓ 创建空书籍结果: {result}")
    
    if result:
        print(f"✓ 成功创建空书籍，ID: {result}")
        empty_book_id = result
    else:
        print(f"✗ 创建空书籍失败")
        empty_book_id = None
    
    # 测试正常创建 - 包含完整内容的书籍
    print("\n🔹 测试创建包含完整内容的书籍")
    
    # 创建测试概念
    concept1 = Concept(
        introduction="这是第一个概念的介绍",
        explanation="这是第一个概念的详细解释",
        conclusion="这是第一个概念的结论"
    )
    
    concept2 = Concept(
        introduction="这是第二个概念的介绍",
        explanation="这是第二个概念的详细解释",
        conclusion="这是第二个概念的结论"
    )
    
    # 创建测试小节
    section1 = Section(
        title="第一小节",
        introduction="第一小节的介绍",
        concepts=[concept1, concept2]
    )
    
    section2 = Section(
        title="第二小节",
        introduction="第二小节的介绍",
        concepts=[concept1]
    )
    
    # 创建测试章节
    chapter1 = Chapter(
        title="第一章",
        introduction="第一章的介绍",
        sections=[section1, section2]
    )
    
    chapter2 = Chapter(
        title="第二章",
        introduction="第二章的介绍",
        sections=[section1]
    )
    
    # 创建完整书籍
    full_book = Book(
        id="",  # ID将被自动生成
        title="完整测试书籍",
        chapters=[chapter1, chapter2]
    )
    
    result = await new_book(full_book)
    print(f"✓ 创建完整书籍结果: {result}")
    
    if result:
        print(f"✓ 成功创建完整书籍，ID: {result}")
        full_book_id = result
    else:
        print(f"✗ 创建完整书籍失败")
        full_book_id = None
    
    # 测试创建多本书籍
    print("\n🔹 测试创建多本书籍")
    book_ids = []
    for i in range(3):
        test_book = Book(
            id="",
            title=f"测试书籍 {i+1}",
            chapters=[]
        )
        result = await new_book(test_book)
        if result:
            book_ids.append(result)
            print(f"✓ 成功创建第{i+1}本书籍，ID: {result}")
        else:
            print(f"✗ 创建第{i+1}本书籍失败")
    
    return {
        "empty_book_id": empty_book_id,
        "full_book_id": full_book_id,
        "multiple_book_ids": book_ids
    }


async def test_get_book(test_book_ids):
    """测试获取书籍"""
    print("\n" + "=" * 50)
    print("测试阶段：获取书籍")
    print("=" * 50)
    
    # 测试获取存在的书籍 - 空书籍
    print("\n🔹 测试获取空书籍")
    if test_book_ids["empty_book_id"]:
        result = await get_book(test_book_ids["empty_book_id"])
        if isinstance(result, Book):
            print(f"✓ 成功获取空书籍，ID: {result.id}")
            print(f"✓ 书籍标题: {result.title}")
            print(f"✓ 章节数量: {len(result.chapters)}")
        else:
            print(f"✗ 获取空书籍失败: {result.get('message', '未知错误')}")
    else:
        print("✗ 无法测试，空书籍ID为空")
    
    # 测试获取存在的书籍 - 完整书籍
    print("\n🔹 测试获取完整书籍")
    if test_book_ids["full_book_id"]:
        result = await get_book(test_book_ids["full_book_id"])
        if isinstance(result, Book):
            print(f"✓ 成功获取完整书籍，ID: {result.id}")
            print(f"✓ 书籍标题: {result.title}")
            print(f"✓ 章节数量: {len(result.chapters)}")
            
            # 验证书籍内容结构
            if result.chapters:
                first_chapter = result.chapters[0]
                print(f"✓ 第一章标题: {first_chapter.title}")
                print(f"✓ 第一章小节数量: {len(first_chapter.sections)}")
                
                if first_chapter.sections:
                    first_section = first_chapter.sections[0]
                    print(f"✓ 第一小节标题: {first_section.title}")
                    print(f"✓ 第一小节概念数量: {len(first_section.concepts)}")
                    
                    if first_section.concepts:
                        first_concept = first_section.concepts[0]
                        print(f"✓ 第一概念介绍: {first_concept.introduction[:30]}...")
        else:
            print(f"✗ 获取完整书籍失败: {result.get('message', '未知错误')}")
    else:
        print("✗ 无法测试，完整书籍ID为空")
    
    # 测试获取多本书籍
    print("\n🔹 测试获取多本书籍")
    for i, book_id in enumerate(test_book_ids["multiple_book_ids"]):
        result = await get_book(book_id)
        if isinstance(result, Book):
            print(f"✓ 成功获取第{i+1}本书籍: {result.title}")
        else:
            print(f"✗ 获取第{i+1}本书籍失败: {result.get('message', '未知错误')}")
    
    # 测试获取不存在的书籍
    print("\n🔹 测试获取不存在的书籍")
    fake_id = "nonexistent_book_id_12345"
    result = await get_book(fake_id)
    if isinstance(result, dict) and result["type"] == "error":
        print(f"✓ 正确处理不存在的书籍: {result['message']}")
    else:
        print(f"✗ 未正确处理不存在的书籍")
    
    # 测试空字符串ID
    print("\n🔹 测试空字符串ID")
    result = await get_book("")
    if isinstance(result, dict) and result["type"] == "error":
        print(f"✓ 正确处理空字符串ID: {result['message']}")
    else:
        print(f"✗ 未正确处理空字符串ID")
    
    # 测试None ID（这会引发异常，需要捕获）
    print("\n🔹 测试None ID")
    try:
        result = await get_book(None)  # type: ignore
        if isinstance(result, dict) and result["type"] == "error":
            print(f"✓ 正确处理None ID: {result['message']}")
        else:
            print(f"✗ 未正确处理None ID")
    except Exception as e:
        print(f"✓ 正确捕获None ID异常: {str(e)[:50]}...")


async def test_book_data_integrity():
    """测试书籍数据完整性"""
    print("\n" + "=" * 50)
    print("测试阶段：书籍数据完整性")
    print("=" * 50)
    
    # 创建一个包含复杂数据的书籍
    print("\n🔹 测试复杂数据结构的完整性")
    
    complex_concepts = []
    for i in range(5):
        concept = Concept(
            introduction=f"概念{i+1}的介绍：这是一个详细的介绍内容",
            explanation=f"概念{i+1}的解释：这包含了复杂的解释逻辑和多层次的分析",
            conclusion=f"概念{i+1}的结论：通过分析我们可以得出重要的结论"
        )
        complex_concepts.append(concept)
    
    complex_sections = []
    for i in range(3):
        section = Section(
            title=f"第{i+1}小节：复杂内容分析",
            introduction=f"第{i+1}小节介绍：这是一个包含多个概念的复杂小节",
            concepts=complex_concepts[i:i+2] if i+2 <= len(complex_concepts) else complex_concepts[i:]
        )
        complex_sections.append(section)
    
    complex_chapters = []
    for i in range(2):
        chapter = Chapter(
            title=f"第{i+1}章：高级主题",
            introduction=f"第{i+1}章介绍：这章涵盖了高级主题和复杂概念",
            sections=complex_sections[i:i+2] if i+2 <= len(complex_sections) else complex_sections[i:]
        )
        complex_chapters.append(chapter)
    
    complex_book = Book(
        id="",
        title="复杂数据结构测试书籍",
        chapters=complex_chapters
    )
    
    # 创建并获取书籍，验证数据完整性
    book_id = await new_book(complex_book)
    if book_id:
        print(f"✓ 成功创建复杂书籍，ID: {book_id}")
        
        # 获取并验证数据完整性
        retrieved_book = await get_book(book_id)
        if isinstance(retrieved_book, Book):
            print(f"✓ 成功获取复杂书籍")
            
            # 验证结构完整性
            if len(retrieved_book.chapters) == len(complex_chapters):
                print(f"✓ 章节数量正确: {len(retrieved_book.chapters)}")
            else:
                print(f"✗ 章节数量不匹配")
            
            # 深度验证数据一致性
            for i, chapter in enumerate(retrieved_book.chapters):
                original_chapter = complex_chapters[i]
                if chapter.title == original_chapter.title:
                    print(f"✓ 第{i+1}章标题一致")
                else:
                    print(f"✗ 第{i+1}章标题不一致")
                
                if len(chapter.sections) == len(original_chapter.sections):
                    print(f"✓ 第{i+1}章小节数量正确")
                else:
                    print(f"✗ 第{i+1}章小节数量不匹配")
                
                for j, section in enumerate(chapter.sections):
                    original_section = original_chapter.sections[j]
                    if len(section.concepts) == len(original_section.concepts):
                        print(f"✓ 第{i+1}章第{j+1}小节概念数量正确")
                    else:
                        print(f"✗ 第{i+1}章第{j+1}小节概念数量不匹配")
        else:
            print(f"✗ 获取复杂书籍失败")
        
        return book_id
    else:
        print(f"✗ 创建复杂书籍失败")
        return None


async def test_encoding():
    """测试中文编码和特殊字符"""
    print("\n" + "=" * 50)
    print("测试阶段：中文编码和特殊字符测试")
    print("=" * 50)
    
    # 测试各种中文内容和特殊字符
    print("\n🔹 测试中文编码")
    
    chinese_concept = Concept(
        introduction="这是一个包含中文的概念介绍：学习、理解、掌握知识的重要性。",
        explanation="详细解释：通过系统性的学习方法，我们可以更好地理解复杂的概念。包含特殊字符：《》【】""''—…",
        conclusion="结论：教育是人类进步的阶梯，知识改变命运。"
    )
    
    emoji_concept = Concept(
        introduction="表情符号测试：📚📖📝✏️🎓",
        explanation="多语言测试：Hello 你好 こんにちは 안녕하세요 Привет",
        conclusion="数字和符号：2025年7月31日，温度25℃，概率95%，价格￥199.99"
    )
    
    special_section = Section(
        title="特殊字符小节：测试各种编码情况",
        introduction="这个小节专门测试特殊字符的处理能力",
        concepts=[chinese_concept, emoji_concept]
    )
    
    encoding_chapter = Chapter(
        title="编码测试章节",
        introduction="本章专门测试各种字符编码的兼容性",
        sections=[special_section]
    )
    
    encoding_book = Book(
        id="",
        title="编码测试书籍：中文、英文、特殊字符混合",
        chapters=[encoding_chapter]
    )
    
    # 创建并验证编码
    book_id = await new_book(encoding_book)
    if book_id:
        print(f"✓ 成功创建编码测试书籍，ID: {book_id}")
        
        # 获取并验证编码正确性
        result = await get_book(book_id)
        if isinstance(result, Book):
            print(f"✓ 书籍标题编码正确: {result.title}")
            
            if result.chapters:
                chapter = result.chapters[0]
                print(f"✓ 章节标题编码正确: {chapter.title}")
                
                if chapter.sections:
                    section = chapter.sections[0]
                    print(f"✓ 小节标题编码正确: {section.title}")
                    
                    for i, concept in enumerate(section.concepts):
                        print(f"✓ 概念{i+1}介绍编码正确: {concept.introduction[:40]}...")
                        print(f"✓ 概念{i+1}解释编码正确: {concept.explanation[:40]}...")
                        print(f"✓ 概念{i+1}结论编码正确: {concept.conclusion[:40]}...")
        else:
            print(f"✗ 获取编码测试书籍失败")
        
        print(f"\n✓ 编码测试完成，保留书籍 {book_id} 用于手动验证数据库文件")
        return book_id
    else:
        print(f"✗ 创建编码测试书籍失败")
        return None


async def test_edge_cases():
    """测试边界情况"""
    print("\n" + "=" * 50)
    print("测试阶段：边界情况测试")
    print("=" * 50)
    
    test_book_ids = []
    
    # 测试最小有效数据
    print("\n🔹 测试最小有效数据")
    minimal_book = Book(
        id="",
        title="最小书籍",
        chapters=[]
    )
    
    book_id = await new_book(minimal_book)
    if book_id:
        test_book_ids.append(book_id)
        print(f"✓ 成功创建最小书籍")
        
        result = await get_book(book_id)
        if isinstance(result, Book):
            print(f"✓ 最小书籍数据验证通过")
        else:
            print(f"✗ 最小书籍数据验证失败")
    
    # 测试单个字符的内容
    print("\n🔹 测试单个字符内容")
    single_char_concept = Concept(
        introduction="a",
        explanation="b",
        conclusion="c"
    )
    
    single_char_section = Section(
        title="x",
        introduction="y",
        concepts=[single_char_concept]
    )
    
    single_char_chapter = Chapter(
        title="z",
        introduction="w",
        sections=[single_char_section]
    )
    
    single_char_book = Book(
        id="",
        title="单",
        chapters=[single_char_chapter]
    )
    
    book_id = await new_book(single_char_book)
    if book_id:
        test_book_ids.append(book_id)
        print(f"✓ 成功创建单字符书籍")
        
        result = await get_book(book_id)
        if isinstance(result, Book):
            print(f"✓ 单字符书籍数据验证通过")
        else:
            print(f"✗ 单字符书籍数据验证失败")
    
    # 测试非常长的内容
    print("\n🔹 测试长内容")
    long_text = "这是一个非常长的文本内容，" * 100  # 重复100次
    
    long_concept = Concept(
        introduction=long_text,
        explanation=long_text,
        conclusion=long_text
    )
    
    long_section = Section(
        title="长内容小节",
        introduction=long_text,
        concepts=[long_concept]
    )
    
    long_chapter = Chapter(
        title="长内容章节",
        introduction=long_text,
        sections=[long_section]
    )
    
    long_book = Book(
        id="",
        title="长内容书籍",
        chapters=[long_chapter]
    )
    
    book_id = await new_book(long_book)
    if book_id:
        test_book_ids.append(book_id)
        print(f"✓ 成功创建长内容书籍")
        
        result = await get_book(book_id)
        if isinstance(result, Book):
            print(f"✓ 长内容书籍数据验证通过")
            # 验证长内容是否完整保存
            if len(result.chapters[0].sections[0].concepts[0].introduction) == len(long_text):
                print(f"✓ 长内容完整性验证通过")
            else:
                print(f"✗ 长内容可能被截断")
        else:
            print(f"✗ 长内容书籍数据验证失败")
    
    return test_book_ids


async def test_concurrent_operations():
    """测试并发操作"""
    print("\n" + "=" * 50)
    print("测试阶段：并发操作测试")
    print("=" * 50)
    
    # 测试并发创建书籍
    print("\n🔹 测试并发创建书籍")
    
    async def create_test_book(index):
        book = Book(
            id="",
            title=f"并发测试书籍 {index}",
            chapters=[]
        )
        return await new_book(book)
    
    # 并发创建10本书
    tasks = [create_test_book(i) for i in range(10)]
    results = await asyncio.gather(*tasks)
    
    successful_creates = [r for r in results if r is not None]
    print(f"✓ 并发创建结果: {len(successful_creates)}/10 成功")
    
    # 验证所有书籍ID是唯一的
    unique_ids = set(successful_creates)
    if len(unique_ids) == len(successful_creates):
        print(f"✓ 所有并发创建的书籍ID都是唯一的")
    else:
        print(f"✗ 发现重复的书籍ID")
    
    # 测试并发获取书籍
    print("\n🔹 测试并发获取书籍")
    
    async def get_test_book(book_id):
        return await get_book(book_id)
    
    if successful_creates:
        # 并发获取所有创建的书籍
        get_tasks = [get_test_book(book_id) for book_id in successful_creates]
        get_results = await asyncio.gather(*get_tasks)
        
        successful_gets = [r for r in get_results if isinstance(r, Book)]
        print(f"✓ 并发获取结果: {len(successful_gets)}/{len(successful_creates)} 成功")
        
        # 验证获取的书籍数据正确性
        for i, result in enumerate(get_results):
            if isinstance(result, Book):
                expected_title = f"并发测试书籍 {i}"
                if expected_title in result.title:
                    print(f"✓ 并发获取的书籍{i}数据正确")
                else:
                    print(f"✗ 并发获取的书籍{i}数据可能错误")
    
    return successful_creates


async def test_delete_book():
    """测试删除书籍功能"""
    print("\n" + "=" * 50)
    print("测试阶段：删除书籍功能")
    print("=" * 50)
    
    # 首先创建一本测试书籍用于删除
    print("\n🔹 创建用于删除测试的书籍")
    test_book = Book(
        id="",
        title="待删除测试书籍",
        chapters=[]
    )
    
    book_id = await new_book(test_book)
    if book_id:
        print(f"✓ 成功创建待删除书籍，ID: {book_id}")
        
        # 验证书籍存在
        result = await get_book(book_id)
        if isinstance(result, Book):
            print(f"✓ 验证书籍存在: {result.title}")
        else:
            print(f"✗ 创建的书籍无法获取")
            return
        
        # 测试删除存在的书籍
        print(f"\n🔹 测试删除存在的书籍")
        delete_result = await delete_book(book_id)
        if delete_result["type"] == "success":
            print(f"✓ 成功删除书籍: {delete_result['message']}")
            
            # 验证书籍确实被删除
            check_result = await get_book(book_id)
            if isinstance(check_result, dict) and check_result["type"] == "error":
                print(f"✓ 验证书籍已被删除")
            else:
                print(f"✗ 书籍删除后仍然存在")
        else:
            print(f"✗ 删除书籍失败: {delete_result['message']}")
    else:
        print(f"✗ 无法创建测试书籍")
    
    # 测试删除不存在的书籍
    print(f"\n🔹 测试删除不存在的书籍")
    fake_id = "nonexistent_book_id_12345"
    result = await delete_book(fake_id)
    if result["type"] == "error":
        print(f"✓ 正确处理删除不存在的书籍: {result['message']}")
    else:
        print(f"✗ 未正确处理删除不存在的书籍")
    
    # 测试删除空字符串ID
    print(f"\n🔹 测试删除空字符串ID")
    result = await delete_book("")
    if result["type"] == "error":
        print(f"✓ 正确处理删除空字符串ID: {result['message']}")
    else:
        print(f"✗ 未正确处理删除空字符串ID")
    
    # 测试删除None ID
    print(f"\n🔹 测试删除None ID")
    try:
        result = await delete_book(None)  # type: ignore
        if result["type"] == "error":
            print(f"✓ 正确处理删除None ID: {result['message']}")
        else:
            print(f"✗ 未正确处理删除None ID")
    except Exception as e:
        print(f"✓ 正确捕获删除None ID异常: {str(e)[:50]}...")


async def cleanup_test_data(book_ids_to_cleanup):
    """清理测试数据"""
    print("\n" + "=" * 50)
    print("测试阶段：清理测试数据")
    print("=" * 50)
    
    # 现在可以使用删除功能清理测试数据
    print("\n🔹 清理测试数据")
    
    all_book_ids = []
    for book_id_group in book_ids_to_cleanup:
        if isinstance(book_id_group, dict):
            # 处理字典类型的书籍ID组（例如test_new_book返回的字典）
            if "empty_book_id" in book_id_group and book_id_group["empty_book_id"]:
                all_book_ids.append(book_id_group["empty_book_id"])
            if "full_book_id" in book_id_group and book_id_group["full_book_id"]:
                all_book_ids.append(book_id_group["full_book_id"])
            if "multiple_book_ids" in book_id_group and book_id_group["multiple_book_ids"]:
                all_book_ids.extend(book_id_group["multiple_book_ids"])
        elif isinstance(book_id_group, list):
            all_book_ids.extend(book_id_group)
        elif book_id_group:
            all_book_ids.append(book_id_group)
    
    deleted_count = 0
    for book_id in all_book_ids:
        if book_id:  # 确保book_id不为None
            result = await delete_book(book_id)
            if result["type"] == "success":
                deleted_count += 1
                print(f"✓ 清理书籍: {book_id}")
            else:
                print(f"⚠️  无法清理书籍 {book_id}: {result['message']}")
    
    print(f"✓ 成功清理 {deleted_count} 本测试书籍")
    
    # 验证清理结果
    remaining_count = 0
    for book_id in all_book_ids:
        if book_id:
            result = await get_book(book_id)
            if isinstance(result, Book):
                remaining_count += 1
    
    print(f"✓ 清理后剩余 {remaining_count} 本书籍在数据库中")
    
    return deleted_count


async def test_comprehensive_workflow():
    """综合测试工作流"""
    print("\n" + "=" * 60)
    print("开始综合测试工作流")
    print("=" * 60)
    
    all_book_ids = []
    
    # 创建一个复杂的工作流测试
    print("\n🔹 复杂工作流测试")
    
    # 步骤1：创建一系列相关书籍
    series_books = []
    for i in range(3):
        concepts = []
        for j in range(2):
            concept = Concept(
                introduction=f"系列{i+1}概念{j+1}介绍",
                explanation=f"系列{i+1}概念{j+1}详细解释",
                conclusion=f"系列{i+1}概念{j+1}重要结论"
            )
            concepts.append(concept)
        
        sections = []
        for j in range(2):
            section = Section(
                title=f"系列{i+1}第{j+1}节",
                introduction=f"系列{i+1}第{j+1}节介绍",
                concepts=concepts
            )
            sections.append(section)
        
        chapters = []
        for j in range(2):
            chapter = Chapter(
                title=f"系列{i+1}第{j+1}章",
                introduction=f"系列{i+1}第{j+1}章介绍",
                sections=sections
            )
            chapters.append(chapter)
        
        book = Book(
            id="",
            title=f"学习系列第{i+1}册：基础到进阶",
            chapters=chapters
        )
        
        book_id = await new_book(book)
        if book_id:
            series_books.append(book_id)
            print(f"✓ 创建系列书籍{i+1}，ID: {book_id}")
    
    all_book_ids.append(series_books)
    
    # 步骤2：验证系列书籍的完整性
    print(f"\n🔹 验证系列书籍完整性")
    for i, book_id in enumerate(series_books):
        result = await get_book(book_id)
        if isinstance(result, Book):
            # 验证结构完整性
            chapter_count = len(result.chapters)
            section_count = sum(len(ch.sections) for ch in result.chapters)
            concept_count = sum(len(sec.concepts) for ch in result.chapters for sec in ch.sections)
            
            print(f"✓ 系列书籍{i+1}: {chapter_count}章, {section_count}节, {concept_count}概念")
        else:
            print(f"✗ 系列书籍{i+1}验证失败")
    
    # 步骤3：性能测试
    print(f"\n🔹 简单性能测试")
    start_time = time.time()
    
    # 快速创建和获取测试
    perf_book = Book(
        id="",
        title="性能测试书籍",
        chapters=[]
    )
    
    perf_book_id = await new_book(perf_book)
    if perf_book_id:
        result = await get_book(perf_book_id)
        end_time = time.time()
        
        if isinstance(result, Book):
            print(f"✓ 性能测试完成，耗时: {(end_time - start_time)*1000:.2f}ms")
            all_book_ids.append([perf_book_id])
        else:
            print(f"✗ 性能测试失败")
    
    return all_book_ids


async def main():
    """主测试函数"""
    print("开始书籍数据库操作测试")
    print("当前时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    try:
        all_test_book_ids = []
        
        # 基础功能测试
        test_book_ids = await test_new_book()
        all_test_book_ids.append(test_book_ids)
        
        await test_get_book(test_book_ids)
        
        # 删除功能测试
        await test_delete_book()
        
        # 数据完整性测试
        integrity_book_id = await test_book_data_integrity()
        if integrity_book_id:
            all_test_book_ids.append([integrity_book_id])
        
        # 编码测试
        encoding_book_id = await test_encoding()
        if encoding_book_id:
            all_test_book_ids.append([encoding_book_id])
        
        # 边界情况测试
        edge_case_book_ids = await test_edge_cases()
        if edge_case_book_ids:
            all_test_book_ids.append(edge_case_book_ids)
        
        # 并发操作测试
        concurrent_book_ids = await test_concurrent_operations()
        if concurrent_book_ids:
            all_test_book_ids.append(concurrent_book_ids)
        
        # 综合测试
        workflow_book_ids = await test_comprehensive_workflow()
        all_test_book_ids.extend(workflow_book_ids)
        
        # 清理测试（实际上是验证数据存在性）
        await cleanup_test_data(all_test_book_ids)
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        print("测试总结：")
        print("✓ 书籍创建功能测试")
        print("✓ 书籍获取功能测试")
        print("✓ 书籍删除功能测试")
        print("✓ 数据完整性验证")
        print("✓ 中文编码和特殊字符测试")
        print("✓ 边界情况处理测试")
        print("✓ 并发操作安全性测试")
        print("✓ 错误处理逻辑验证")
        print("✓ 综合工作流测试")
        
    except Exception as e:
        print(f"\n❌ 测试过程中发生异常: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
