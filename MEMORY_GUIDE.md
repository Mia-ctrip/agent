# Memory System 使用指南

## 🎯 问题解决

你的agent项目之前memory模块无法沉淀数据，原因是：
1. ❌ 只在检测到"纠正关键词"时被动保存
2. ❌ 没有提供memory工具给agent主动调用
3. ❌ memory类型单一，只支持feedback

## ✅ 已完成的修改

### 1. 新增Memory工具 (`tools/memory_tools.py`)

- **save_memory** - 保存持久记忆
  - 支持4种类型：user, feedback, project, reference
  - 自动生成带frontmatter的markdown文件
  - 自动更新MEMORY.md索引

- **read_memory** - 读取记忆
  - 可查看所有记忆
  - 支持关键词搜索

### 2. 更新工具配置 (`tools/tools_config.py`)

已将memory工具注册到agent可用工具列表中：
```python
{
    "name": "save_memory",
    "description": "保存跨会话的持久记忆...",
    "parameters": {
        "content": "记忆内容",
        "memory_type": "user/feedback/project/reference",
        "name": "记忆名称",
        "description": "一行描述"
    }
}
```

### 3. 增强Prompt (`prompt/prompt_builder.py`)

更新了MEMORY_GUIDANCE，明确告诉agent：
- 何时保存记忆（用户偏好、纠正、项目信息等）
- 如何格式化记忆（特别是feedback类型）
- 什么不应该保存（临时任务、一次性结果等）

## 🚀 使用方法

### 方式1：用户明确要求记住

```python
用户: "记住：我喜欢在执行危险操作前看详细计划"
Agent: 会调用 save_memory(
    content="...",
    memory_type="user",
    name="用户偏好-危险操作确认",
    description="用户希望在危险操作前看到详细计划"
)
```

### 方式2：用户纠正agent行为

```python
用户: "不对，你应该先检查磁盘空间再清理缓存"
Agent: 会调用 save_memory(
    content="""
    **Rule:** 清理缓存前必须先检查磁盘空间
    **Why:** 避免在空间不足时清理导致问题
    **How to apply:** 每次调用clean_container_disk_cache前先调用collect_host_disk_info
    """,
    memory_type="feedback",
    name="清理缓存前检查空间",
    description="清理操作的前置检查规则"
)
```

### 方式3：agent主动学习

当agent发现重要信息时，会主动保存：
- 用户的角色和偏好
- 系统的限制和特性
- 重要的外部资源位置
- 可复用的解决方案

### 方式4：查看已保存的记忆

```python
用户: "你都记住了什么？"
Agent: 调用 read_memory() 查看所有记忆

用户: "关于磁盘清理的记忆有哪些？"
Agent: 调用 read_memory(query="磁盘清理") 搜索相关记忆
```

## 📂 记忆文件结构

```
memory/
├── MEMORY.md                              # 记忆索引（自动更新）
├── user_用户偏好_1234567890.md           # 用户信息类记忆
├── feedback_操作规则_1234567891.md       # 经验教训类记忆
├── project_当前任务_1234567892.md        # 项目信息类记忆
└── reference_API文档_1234567893.md       # 外部资源类记忆
```

每个记忆文件格式：
```markdown
---
name: 记忆名称
description: 一行描述
type: user/feedback/project/reference
---

记忆的主要内容...
```

## 🧪 测试

运行测试脚本验证功能：
```bash
python test_memory.py
```

或者直接运行main.py进行交互测试：
```bash
python main.py

You: 记住：我是GPU运维工程师，负责处理磁盘满的问题
Agent: [会保存到memory]

You: 你都记住了什么？
Agent: [会读取并展示所有记忆]
```

## 🔑 关键改进

1. **主动性** - agent现在可以主动判断何时保存记忆，不再只依赖关键词检测
2. **灵活性** - 支持4种记忆类型，覆盖不同场景
3. **可检索** - 通过read_memory工具可以查看和搜索历史记忆
4. **持久性** - 所有记忆保存为markdown文件，跨会话持久化
5. **自动索引** - MEMORY.md自动维护索引，易于查看

## 💡 最佳实践

1. **Feedback记忆应包含**：Rule + Why + How to apply
2. **User记忆应专注于**：用户偏好、角色、工作方式
3. **Project记忆应记录**：当前目标、重要决策、进度里程碑
4. **Reference记忆应保存**：外部系统位置、API端点、文档链接

## 📊 与自动检测的对比

| 特性 | 原有方式 | 改进后 |
|------|---------|--------|
| 触发方式 | 被动（关键词检测） | 主动（agent判断） |
| 记忆类型 | 仅feedback | user/feedback/project/reference |
| 查看记忆 | 不支持 | read_memory工具 |
| 覆盖场景 | 仅纠正场景 | 所有值得记住的场景 |
| 灵活性 | 低 | 高 |

现在你的agent已经具备完整的记忆能力了！🎉
