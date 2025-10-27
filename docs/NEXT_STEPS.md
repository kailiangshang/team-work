# 下一步操作指南

## ✅ 已完成的工作

架构优化已经完成，所有模块已成功整合到 `team-work/twork/` 目录。

- ✅ 合并了31个模块文件（v0.1 + v0.2）
- ✅ 新增2个模块（estimator, version）
- ✅ 整合文档到 docs/ 目录
- ✅ 创建防重复工具和规范
- ✅ 更新版本到 v0.2.0

## 🚀 立即执行步骤

### 1. 清理冗余文件（可选）

根目录的 `twork/` 目录已经不再需要，所有功能已合并到 `team-work/twork/`。

**清理脚本**:
```bash
cd "/Users/kaiiangs/Desktop/team work"

# 删除根目录的 twork/ 目录
rm -rf twork/

# 删除根目录的冗余文档
rm -f DEPLOYMENT_GUIDE.md
rm -f README_V2_FEATURES.md
rm -f MODULE_MERGE_STRATEGY.md
rm -f IMPLEMENTATION_SUMMARY.md
rm -f PROJECT_COMPLETION_REPORT.md

echo "✅ 清理完成！"
```

**注意**: 清理后只保留 `team-work/` 和 `test_new_features.py`

### 2. 安装依赖

```bash
cd team-work

# 安装 twork 核心库（开发模式）
pip install -e .

# 或者安装所有依赖
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 3. 配置环境变量

```bash
cd team-work

# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置必要的变量
# 必需配置:
# - LLM_API_KEY
# - LLM_API_BASE_URL (可选，默认OpenAI)
# - DATABASE_TYPE (sqlite 或 postgresql)
```

### 4. 测试新功能

```bash
# 运行功能测试
cd "/Users/kaiiangs/Desktop/team work"
python test_new_features.py
```

预期输出：
```
✅ 领域分类测试通过
✅ 模板管理测试通过
✅ 复杂度分析测试通过
✅ 时间估算测试通过
✅ 冲突解决测试通过
✅ 甘特图生成测试通过
✅ 风险分析测试通过
✅ 版本管理测试通过
```

### 5. 启动服务

#### 方式A: Docker部署（推荐）

```bash
cd team-work

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问应用
# 前端: http://localhost:7860
# 后端: http://localhost:8000
# API文档: http://localhost:8000/docs
```

#### 方式B: 本地运行

```bash
# 终端1: 启动后端
cd team-work/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2: 启动前端
cd team-work/frontend
python app.py
```

## 📋 验证清单

完成上述步骤后，请验证：

- [ ] 根目录只剩 `team-work/` 和 `test_new_features.py`
- [ ] `team-work/twork/` 包含31个模块文件
- [ ] `team-work/docs/` 包含所有文档
- [ ] 环境变量已配置
- [ ] 依赖已安装
- [ ] 测试脚本运行成功
- [ ] 服务启动成功
- [ ] 可以访问前端界面

## 🔍 问题排查

### 问题1: 导入错误 `ModuleNotFoundError: No module named 'twork'`

**解决方案**:
```bash
cd team-work
pip install -e .
```

### 问题2: 依赖缺失 `ModuleNotFoundError: No module named 'XXX'`

**解决方案**:
```bash
pip install -r backend/requirements.txt
```

### 问题3: 数据库连接错误

**解决方案**:
1. 检查 `.env` 文件中的数据库配置
2. 如果使用SQLite，确保 `data/db/` 目录存在
3. 如果使用PostgreSQL，确保服务已启动

### 问题4: LLM API错误

**解决方案**:
1. 检查 `.env` 文件中的 `LLM_API_KEY`
2. 检查 `LLM_API_BASE_URL` 是否正确
3. 验证API密钥是否有效

## 📚 参考文档

完成后，建议阅读：

1. [快速开始指南](./QUICKSTART.md) - 详细的使用教程
2. [功能说明](./FEATURES.md) - v0.2.0新功能介绍
3. [模块清单](./MODULES.md) - 防止重复造轮子
4. [部署指南](./DEPLOYMENT_GUIDE.md) - 生产环境部署
5. [架构优化报告](./ARCHITECTURE_OPTIMIZATION_REPORT.md) - 完整的优化记录

## 🎯 后续改进建议

### 短期（1-2周）

1. **添加单元测试**
   - 为每个模块编写测试
   - 目标覆盖率 > 80%
   - 配置CI自动测试

2. **完善API文档**
   - 为每个接口添加详细说明
   - 添加请求/响应示例
   - 更新Swagger文档

3. **优化前端界面**
   - 改进用户体验
   - 添加错误提示
   - 优化加载速度

### 中期（1-2月）

1. **性能优化**
   - 添加Redis缓存
   - 实现异步任务队列
   - 优化数据库查询

2. **功能扩展**
   - 添加更多领域模板
   - 支持更多文档格式
   - 增强可视化功能

3. **多语言支持**
   - 国际化（i18n）
   - 支持英文界面
   - 多语言文档

### 长期（3-6月）

1. **前端升级**
   - Gradio → React + TypeScript
   - 集成Ant Design
   - 响应式设计

2. **企业级功能**
   - 多用户支持
   - 权限管理
   - 审计日志

3. **集成能力**
   - 第三方工具集成（Jira、Trello等）
   - Webhook支持
   - RESTful API完善

## 💡 开发规范

### 添加新功能前

1. ✅ 检查 `docs/MODULES.md` 功能清单
2. ✅ 搜索现有代码避免重复
3. ✅ 运行 `python scripts/check_duplication.py`
4. ✅ 确认功能归属模块
5. ✅ 遵循依赖方向规则

### 代码提交规范

```bash
# 提交格式
git commit -m "feat(module): 功能描述

重复性检查：
- 已搜索 twork/xxx 无相同功能
- 复用了 twork/utils/common.py 的 xxx 函数
- 更新了 docs/MODULES.md
"
```

### Code Review检查点

- [ ] 无重复代码
- [ ] 可提取通用函数
- [ ] 复用现有工具
- [ ] 更新功能清单
- [ ] 符合依赖规范

## 🎉 开始使用

一切准备就绪！现在可以：

1. 上传需求文档
2. 自动生成项目计划
3. 模拟项目执行
4. 导出可视化结果

享受 TeamWork v0.2.0 带来的强大功能！

---

**文档更新**: 2025-10-25  
**版本**: v0.2.0  
**状态**: ✅ 可以开始使用
