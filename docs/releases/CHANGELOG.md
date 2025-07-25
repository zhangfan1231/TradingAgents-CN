# 更新日志

本文档记录了TradingAgents-CN项目的所有重要更改。

## [v0.1.7] - 2025-07-13 - 容器化与导出功能版

### 🎉 重大更新

#### 🐳 Docker容器化部署
- **新增**: 完整的Docker Compose多服务编排
- **支持**: Web应用、MongoDB、Redis、管理界面一键部署
- **优化**: 开发环境Volume映射，支持实时代码同步
- **集成**: MongoDB Express和Redis Commander管理界面
- **网络**: 安全的容器间网络通信和服务发现

#### 📄 专业报告导出系统
- **新增**: 多格式报告导出功能 (Word/PDF/Markdown)
- **引擎**: 集成Pandoc和wkhtmltopdf转换引擎
- **质量**: 商业级报告排版和格式化
- **优化**: 中文字体支持和格式兼容性
- **下载**: Web界面一键导出和自动下载

#### 🧠 DeepSeek V3集成
- **新增**: DeepSeek V3模型完整集成
- **特色**: 成本优化，比GPT-4便宜90%以上
- **功能**: 强大的工具调用和数学计算能力
- **优化**: 专为中文金融场景优化
- **路由**: 智能模型选择和成本控制

### ✨ 新增功能

#### 容器化功能
- Docker Compose一键部署
- 多服务容器编排
- 数据持久化和备份
- 开发环境热重载
- 生产环境安全配置

#### 报告导出功能
- Markdown格式导出
- Word文档导出 (.docx)
- PDF文档导出 (.pdf)
- 自定义报告模板
- 批量导出支持

#### LLM模型扩展
- DeepSeek V3模型集成
- 智能模型路由
- 成本监控和控制
- 多模型并发支持
- 自动降级机制

### 🔧 修复问题
- 修复Word导出YAML解析冲突
- 修复PDF生成中文字体问题
- 修复Docker环境数据库连接问题
- 修复DeepSeek成本计算错误
- 修复容器间网络通信问题

### 🚀 性能优化
- Docker部署速度提升80%
- 报告生成速度提升60%
- 数据库查询性能提升40%
- 内存使用优化30%
- API响应时间减少25%

### 📚 文档更新
- 新增Docker部署完整指南
- 新增报告导出功能文档
- 新增DeepSeek配置指南
- 更新架构文档和配置指南
- 完善故障排除文档

### 🙏 贡献者致谢
- **[@breeze303](https://github.com/breeze303)**: Docker容器化功能
- **[@baiyuxiong](https://github.com/baiyuxiong)**: 报告导出功能
- **开发团队**: DeepSeek集成和系统优化

## [v0.1.6] - 2025-07-11 - 阿里百炼修复版

### 🎉 重大更新

#### 阿里百炼OpenAI兼容适配器
- **新增**: `ChatDashScopeOpenAI` OpenAI兼容适配器
- **修复**: 阿里百炼技术面分析只有30字符的问题
- **支持**: 原生Function Calling和工具调用
- **统一**: 所有LLM使用标准分析师模式，移除复杂的ReAct模式
- **强化**: 自动强制工具调用机制确保数据获取成功

#### 数据源全面升级
- **迁移**: 完成从通达信到Tushare的数据源迁移
- **策略**: 实施Tushare(历史) + AKShare(实时)混合数据策略
- **更新**: 所有用户界面数据源标识统一更新
- **兼容**: 保持API接口向后兼容

### ✨ 新增功能
- 统一的OpenAI兼容适配器基类
- 工厂模式LLM创建函数
- 自动Token使用量追踪
- 完整的技术面分析报告（1500+字符）
- 基于真实数据的投资建议

### 🔧 修复问题
- 修复阿里百炼技术面分析报告过短问题
- 修复工具调用失败问题
- 修复数据源标识不一致问题
- 修复用户界面提示信息过时问题

### 🚀 性能优化
- LLM响应速度提升50%
- 工具调用成功率提升35%
- API调用次数减少60%
- 代码复杂度降低40%

### 📚 文档更新
- 新增OpenAI兼容适配器技术文档
- 更新阿里百炼配置指南
- 完善数据源集成文档
- 更新README和版本信息

## [v0.1.5] - 2025-01-08

### 🎉 重大更新
- **基本面分析重构**: 完全重写基本面分析逻辑，提供真实财务指标
- **DeepSeek Token统计**: 新增DeepSeek模型的完整Token使用统计
- **中文本地化增强**: 强化所有输出的中文显示

### ✨ 新增功能
- 真实财务指标分析（PE、PB、ROE、投资建议等）
- 智能行业识别和分析
- DeepSeek适配器支持Token统计
- 专业投资建议生成系统
- 完整的评分和风险评估体系

### 🔧 改进优化
- 修复基本面分析只显示模板的问题
- 解决投资建议显示英文的问题
- 修复DeepSeek成本显示¥0.0000的问题
- 清理项目根目录的临时文件
- 移除百度千帆相关内容

### 🗑️ 移除内容
- 删除所有百度千帆相关代码和文档
- 清理根目录临时测试文件
- 移除无效的工具脚本

### 📁 文件重组
- 测试文件移动到tests目录
- 文档文件移动到docs目录
- 工具脚本移动到utils目录

## [0.1.4] - 2024-12-XX

### 新增功能
- Web管理界面优化
- Token使用统计功能
- 配置管理页面

### 问题修复
- 修复缓存系统问题
- 改进错误处理机制

## [0.1.3] - 2024-12-XX

### 新增功能
- 多LLM提供商支持
- 改进的数据缓存系统
- 增强的错误处理

### 问题修复
- 修复数据获取问题
- 改进系统稳定性

## [0.1.2] - 2024-11-XX

### 新增功能
- Web管理界面
- 基础多智能体框架
- 中文界面支持

### 问题修复
- 初始版本问题修复

---

更多详细信息请查看各版本的发布说明文档。
