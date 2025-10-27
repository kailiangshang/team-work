# StructureFactory 测试环境

本目录包含 StructureFactory 的完整测试环境，用于验证文档解析、需求分析和WBS生成功能。

## 目录结构

```
test-parser/
├── data/                   # 测试数据目录
│   ├── sample.md          # Markdown格式测试文档
│   ├── sample.txt         # 纯文本格式测试文档
│   ├── sample.pdf         # PDF格式测试文档（自动生成）
│   ├── sample.docx        # Word格式测试文档（自动生成）
│   └── sample.pptx        # PowerPoint格式测试文档（自动生成）
├── Dockerfile             # Docker镜像配置
├── docker-compose.yml     # Docker Compose配置
├── requirements.txt       # Python依赖
├── test.py               # 测试脚本
└── README.md             # 本文件
```

## 快速开始

### 方式1：使用Docker（推荐）

1. **构建镜像**
   ```bash
   docker-compose build
   ```

2. **运行测试（不使用LLM）**
   ```bash
   docker-compose run test-parser
   ```

3. **运行测试（使用LLM）**
   ```bash
   # 设置环境变量
   export OPENAI_API_KEY=your-api-key
   export OPENAI_API_BASE=https://api.openai.com/v1
   
   # 运行测试
   docker-compose run test-parser
   ```

### 方式2：本地运行

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **运行测试**
   ```bash
   cd /path/to/test-parser
   python test.py
   ```

3. **使用LLM测试**
   ```bash
   export OPENAI_API_KEY=your-api-key
   python test.py
   ```

## 测试内容

测试脚本包含以下测试用例：

### 测试1：创建测试文档
- 自动生成PDF、DOCX、PPTX格式的测试文档
- 包含不同类型的项目需求内容

### 测试2：文档解析功能
- 测试所有支持的文档格式（PDF、DOCX、PPTX、MD、TXT）
- 验证章节提取是否正确
- 显示解析结果预览

### 测试3：StructureFactory基本功能
- 测试工厂初始化
- 测试文档解析和缓存机制
- 不需要LLM即可运行

### 测试4：StructureFactory完整流程
- 测试需求提取和领域识别
- 测试WBS任务分解
- 需要配置OPENAI_API_KEY

## 测试输出

测试运行后会生成以下文件：

- `cache/` - 文档解析缓存
- `output_result.json` - 完整的分析结果（包含需求和WBS）

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `OPENAI_API_KEY` | OpenAI API密钥 | 无 |
| `OPENAI_API_BASE` | OpenAI API地址 | https://api.openai.com/v1 |

### 测试数据

测试数据位于 `data/` 目录：

- **sample.md** - 团队协作系统需求（软件开发领域）
- **sample.txt** - 电商平台需求（软件开发领域）
- **sample.pdf** - 智能家居系统需求（自动生成）
- **sample.docx** - 在线教育平台需求（自动生成）
- **sample.pptx** - 智慧物流系统需求（自动生成）

## 预期结果

成功运行测试后，您应该看到：

```
==============================================================
StructureFactory 测试套件
==============================================================

==============================================================
正在创建测试文档...
==============================================================
✓ 创建PDF文档: ./data/sample.pdf
✓ 创建DOCX文档: ./data/sample.docx
✓ 创建PPTX文档: ./data/sample.pptx

==============================================================
测试1: 文档解析功能
==============================================================
测试文件: sample.md
  ✓ 解析成功，共 X 个章节

...（其他测试结果）

==============================================================
测试完成！
==============================================================
```

## 故障排除

### 问题1：PDF/DOCX/PPTX生成失败

**原因**：缺少对应的Python库

**解决**：
```bash
pip install reportlab python-docx python-pptx
```

### 问题2：LLM测试跳过

**原因**：未配置OPENAI_API_KEY

**解决**：
```bash
export OPENAI_API_KEY=your-api-key
```

### 问题3：导入模块失败

**原因**：Python路径配置问题

**解决**：
```bash
# 确保在正确的目录运行
cd /path/to/test-parser
export PYTHONPATH=/path/to/team-work
python test.py
```

## 自定义测试

您可以修改 `test.py` 来添加自己的测试用例：

```python
def test_custom_document():
    """自定义测试"""
    factory = StructureUnderstandFactory(
        project_id="my-test",
        original_file_path="./data/my_doc.pdf"
    )
    # 配置和运行...
    result = factory.run()
```

## 下一步

- 查看 `../../parser/README.md` 了解更多API文档
- 查看 `output_result.json` 了解输出格式
- 修改测试数据测试不同类型的项目需求
