#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Google模型工具调用统一处理器

解决Google模型在工具调用时result.content为空的问题，
提供统一的工具调用处理逻辑供所有分析师使用。
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

logger = logging.getLogger(__name__)

class GoogleToolCallHandler:
    """Google模型工具调用统一处理器"""
    
    @staticmethod
    def is_google_model(llm) -> bool:
        """检查是否为Google模型"""
        return 'Google' in llm.__class__.__name__ or 'ChatGoogleOpenAI' in llm.__class__.__name__
    
    @staticmethod
    def handle_google_tool_calls(
        result: AIMessage,
        llm: Any,
        tools: List[Any],
        state: Dict[str, Any],
        analysis_prompt_template: str,
        analyst_name: str = "分析师"
    ) -> Tuple[str, List[Any]]:
        """
        统一处理Google模型的工具调用
        
        Args:
            result: LLM的第一次调用结果
            llm: 语言模型实例
            tools: 可用工具列表
            state: 当前状态
            analysis_prompt_template: 分析提示词模板
            analyst_name: 分析师名称
            
        Returns:
            Tuple[str, List[Any]]: (分析报告, 消息列表)
        """
        
        # 验证输入参数
        logger.info(f"[{analyst_name}] 🔍 开始Google工具调用处理...")
        logger.debug(f"[{analyst_name}] 🔍 LLM类型: {llm.__class__.__name__}")
        logger.debug(f"[{analyst_name}] 🔍 工具数量: {len(tools) if tools else 0}")
        logger.debug(f"[{analyst_name}] 🔍 状态类型: {type(state).__name__ if state else None}")
        
        if not GoogleToolCallHandler.is_google_model(llm):
            logger.warning(f"[{analyst_name}] ⚠️ 非Google模型，跳过特殊处理")
            logger.debug(f"[{analyst_name}] 🔍 模型检查失败: {llm.__class__.__name__}")
            # 非Google模型，返回原始内容
            return result.content, [result]
        
        logger.info(f"[{analyst_name}] ✅ 确认为Google模型")
        logger.debug(f"[{analyst_name}] 🔍 结果类型: {type(result).__name__}")
        logger.debug(f"[{analyst_name}] 🔍 结果属性: {[attr for attr in dir(result) if not attr.startswith('_')]}")
        
        # 检查API调用是否成功
        if not hasattr(result, 'content'):
            logger.error(f"[{analyst_name}] ❌ Google模型API调用失败，无返回内容")
            logger.debug(f"[{analyst_name}] 🔍 结果对象缺少content属性")
            return "Google模型API调用失败", []
        
        # 检查是否有工具调用
        if not hasattr(result, 'tool_calls'):
            logger.warning(f"[{analyst_name}] ⚠️ 结果对象没有tool_calls属性")
            logger.debug(f"[{analyst_name}] 🔍 可用属性: {[attr for attr in dir(result) if not attr.startswith('_')]}")
            return result.content, [result]
        
        if not result.tool_calls:
            # 改进：提供更详细的诊断信息
            logger.info(f"[{analyst_name}] ℹ️ Google模型未调用工具，可能原因：")
            logger.info(f"[{analyst_name}]   - 输入消息为空或格式不正确")
            logger.info(f"[{analyst_name}]   - 模型认为不需要调用工具")
            logger.info(f"[{analyst_name}]   - 工具绑定可能存在问题")
            
            # 检查输入消息
            if "messages" in state:
                messages = state["messages"]
                if not messages:
                    logger.warning(f"[{analyst_name}] ⚠️ 输入消息列表为空")
                else:
                    logger.info(f"[{analyst_name}] 📝 输入消息数量: {len(messages)}")
                    for i, msg in enumerate(messages):
                        msg_type = type(msg).__name__
                        content_preview = str(msg.content)[:100] if hasattr(msg, 'content') else "无内容"
                        logger.info(f"[{analyst_name}]   消息 {i+1}: {msg_type} - {content_preview}...")
            
            # 检查内容是否为分析报告
            content = result.content
            logger.info(f"[{analyst_name}] 🔍 检查返回内容是否为分析报告...")
            logger.debug(f"[{analyst_name}] 🔍 内容类型: {type(content)}")
            logger.debug(f"[{analyst_name}] 🔍 内容长度: {len(content) if content else 0}")
            
            # 检查内容是否包含分析报告的特征
            is_analysis_report = False
            analysis_keywords = ["分析", "报告", "总结", "评估", "建议", "风险", "趋势", "市场", "股票", "投资"]
            
            if content:
                # 检查内容长度和关键词
                if len(content) > 200:  # 假设分析报告至少有200个字符
                    keyword_count = sum(1 for keyword in analysis_keywords if keyword in content)
                    is_analysis_report = keyword_count >= 3  # 至少包含3个关键词
                
                logger.info(f"[{analyst_name}] 🔍 内容判断为{'分析报告' if is_analysis_report else '非分析报告'}")
                
                if is_analysis_report:
                    logger.info(f"[{analyst_name}] ✅ Google模型直接返回了分析报告，长度: {len(content)} 字符")
                    return content, [result]
            
            # 返回原始内容，但添加说明
            return result.content, [result]
        
        logger.info(f"[{analyst_name}] 🔧 Google模型调用了 {len(result.tool_calls)} 个工具")
        
        # 记录工具调用详情
        for i, tool_call in enumerate(result.tool_calls):
            logger.info(f"[{analyst_name}] 工具 {i+1}:")
            logger.info(f"[{analyst_name}]   ID: {tool_call.get('id', 'N/A')}")
            logger.info(f"[{analyst_name}]   名称: {tool_call.get('name', 'N/A')}")
            logger.info(f"[{analyst_name}]   参数: {tool_call.get('args', {})}")
        
        try:
            # 执行工具调用
            tool_messages = []
            tool_results = []
            
            logger.info(f"[{analyst_name}] 🔧 开始执行 {len(result.tool_calls)} 个工具调用...")
            
            for i, tool_call in enumerate(result.tool_calls):
                tool_name = tool_call.get('name')
                tool_args = tool_call.get('args', {})
                tool_id = tool_call.get('id')
                
                logger.info(f"[{analyst_name}] 🛠️ 执行工具 {i+1}/{len(result.tool_calls)}: {tool_name}")
                logger.info(f"[{analyst_name}] 参数: {tool_args}")
                logger.debug(f"[{analyst_name}] 🔧 工具调用详情: {tool_call}")
                
                # 找到对应的工具并执行
                tool_result = None
                available_tools = []
                
                for tool in tools:
                    current_tool_name = GoogleToolCallHandler._get_tool_name(tool)
                    available_tools.append(current_tool_name)
                    
                    if current_tool_name == tool_name:
                        try:
                            logger.debug(f"[{analyst_name}] 🔧 找到工具: {tool.__class__.__name__}")
                            logger.debug(f"[{analyst_name}] 🔧 工具类型检查...")
                            
                            # 检查工具类型并相应调用
                            if hasattr(tool, 'invoke'):
                                # LangChain工具，使用invoke方法
                                logger.info(f"[{analyst_name}] 🚀 正在调用LangChain工具.invoke()...")
                                tool_result = tool.invoke(tool_args)
                                logger.info(f"[{analyst_name}] ✅ LangChain工具执行成功，结果长度: {len(str(tool_result))} 字符")
                                logger.debug(f"[{analyst_name}] 🔧 工具结果类型: {type(tool_result)}")
                            elif callable(tool):
                                # 普通Python函数，直接调用
                                logger.info(f"[{analyst_name}] 🚀 正在调用Python函数工具...")
                                tool_result = tool(**tool_args)
                                logger.info(f"[{analyst_name}] ✅ Python函数工具执行成功，结果长度: {len(str(tool_result))} 字符")
                                logger.debug(f"[{analyst_name}] 🔧 工具结果类型: {type(tool_result)}")
                            else:
                                logger.error(f"[{analyst_name}] ❌ 工具类型不支持: {type(tool)}")
                                tool_result = f"工具类型不支持: {type(tool)}"
                            break
                        except Exception as tool_error:
                            logger.error(f"[{analyst_name}] ❌ 工具执行失败: {tool_error}")
                            logger.error(f"[{analyst_name}] ❌ 异常类型: {type(tool_error).__name__}")
                            logger.error(f"[{analyst_name}] ❌ 异常详情: {str(tool_error)}")
                            
                            # 记录详细的异常堆栈
                            import traceback
                            error_traceback = traceback.format_exc()
                            logger.error(f"[{analyst_name}] ❌ 工具执行异常堆栈:\n{error_traceback}")
                            
                            tool_result = f"工具执行失败: {str(tool_error)}"
                
                logger.debug(f"[{analyst_name}] 🔧 可用工具列表: {available_tools}")
                
                if tool_result is None:
                    tool_result = f"未找到工具: {tool_name}"
                    logger.warning(f"[{analyst_name}] ⚠️ 未找到工具: {tool_name}")
                    logger.debug(f"[{analyst_name}] ⚠️ 工具名称不匹配，期望: {tool_name}, 可用: {available_tools}")
                
                # 创建工具消息
                tool_message = ToolMessage(
                    content=str(tool_result),
                    tool_call_id=tool_id
                )
                tool_messages.append(tool_message)
                tool_results.append(tool_result)
                logger.debug(f"[{analyst_name}] 🔧 创建工具消息，ID: {tool_message.tool_call_id}")
            
            logger.info(f"[{analyst_name}] 🔧 工具调用完成，成功: {len(tool_results)}, 总计: {len(result.tool_calls)}")
            
            # 第二次调用模型生成最终分析报告
            logger.info(f"[{analyst_name}] 🚀 基于工具结果生成最终分析报告...")
            
            # 安全地构建消息序列，确保所有消息都是有效的LangChain消息类型
            safe_messages = []
            
            # 添加历史消息（只保留有效的LangChain消息）
            if "messages" in state and state["messages"]:
                for msg in state["messages"]:
                    try:
                        if hasattr(msg, 'content') and hasattr(msg, '__class__'):
                            # 检查是否是有效的LangChain消息类型
                            msg_class_name = msg.__class__.__name__
                            if msg_class_name in ['HumanMessage', 'AIMessage', 'SystemMessage', 'ToolMessage']:
                                safe_messages.append(msg)
                            else:
                                # 转换为HumanMessage
                                logger.warning(f"[{analyst_name}] ⚠️ 转换非标准消息类型: {msg_class_name}")
                                safe_messages.append(HumanMessage(content=str(msg.content)))
                    except Exception as msg_error:
                        logger.warning(f"[{analyst_name}] ⚠️ 跳过无效消息: {msg_error}")
                        continue
            
            # 添加当前结果（确保是AIMessage）
            if hasattr(result, 'content'):
                safe_messages.append(result)
            
            # 添加工具消息
            safe_messages.extend(tool_messages)
            
            # 添加分析提示
            safe_messages.append(HumanMessage(content=analysis_prompt_template))
            
            # 检查消息序列长度，避免过长
            total_length = sum(len(str(msg.content)) for msg in safe_messages if hasattr(msg, 'content'))
            if total_length > 50000:
                logger.warning(f"[{analyst_name}] ⚠️ 消息序列过长 ({total_length} 字符)，进行优化...")
                
                # 优化策略：保留最重要的消息
                optimized_messages = []
                
                # 保留最后的用户消息
                if safe_messages and isinstance(safe_messages[0], HumanMessage):
                    optimized_messages.append(safe_messages[0])
                
                # 保留工具调用结果
                optimized_messages.append(result)
                
                # 保留工具消息（截断过长的内容）
                for tool_msg in tool_messages:
                    if len(tool_msg.content) > 5000:
                        truncated_content = tool_msg.content[:5000] + "\n\n[注：数据已截断以确保处理效率]"
                        optimized_tool_msg = ToolMessage(
                            content=truncated_content,
                            tool_call_id=tool_msg.tool_call_id
                        )
                        optimized_messages.append(optimized_tool_msg)
                    else:
                        optimized_messages.append(tool_msg)
                
                # 保留分析提示
                optimized_messages.append(HumanMessage(content=analysis_prompt_template))
                
                safe_messages = optimized_messages
                logger.info(f"[{analyst_name}] ✅ 消息序列优化完成，新长度: {sum(len(str(msg.content)) for msg in safe_messages)} 字符")
            
            logger.info(f"[{analyst_name}] 📊 最终消息序列: {len(safe_messages)} 条消息")
            
            # 检查消息序列是否为空
            if not safe_messages:
                logger.error(f"[{analyst_name}] ❌ 消息序列为空，无法生成分析报告")
                tool_summary = "\n\n".join([f"工具结果 {i+1}:\n{str(result)}" for i, result in enumerate(tool_results)])
                report = f"{analyst_name}工具调用完成，获得以下数据：\n\n{tool_summary}"
                return report, [result] + tool_messages
            
            # 生成最终分析报告
            try:
                logger.info(f"[{analyst_name}] 🔄 开始调用Google模型生成最终分析报告...")
                logger.debug(f"[{analyst_name}] 📋 LLM类型: {llm.__class__.__name__}")
                logger.debug(f"[{analyst_name}] 📋 消息数量: {len(safe_messages)}")
                
                # 记录每个消息的类型和长度
                for i, msg in enumerate(safe_messages):
                    msg_type = msg.__class__.__name__
                    msg_length = len(str(msg.content)) if hasattr(msg, 'content') else 0
                    logger.debug(f"[{analyst_name}] 📋 消息 {i+1}: {msg_type}, 长度: {msg_length}")
                
                # 记录分析提示的内容（前200字符）
                analysis_msg = safe_messages[-1] if safe_messages else None
                if analysis_msg and hasattr(analysis_msg, 'content'):
                    prompt_preview = str(analysis_msg.content)[:200] + "..." if len(str(analysis_msg.content)) > 200 else str(analysis_msg.content)
                    logger.debug(f"[{analyst_name}] 📋 分析提示预览: {prompt_preview}")
                
                logger.info(f"[{analyst_name}] 🚀 正在调用LLM.invoke()...")
                final_result = llm.invoke(safe_messages)
                logger.info(f"[{analyst_name}] ✅ LLM.invoke()调用完成")
                
                # 详细检查返回结果
                logger.debug(f"[{analyst_name}] 🔍 检查LLM返回结果...")
                logger.debug(f"[{analyst_name}] 🔍 返回结果类型: {type(final_result)}")
                logger.debug(f"[{analyst_name}] 🔍 返回结果属性: {dir(final_result)}")
                
                if hasattr(final_result, 'content'):
                    content = final_result.content
                    logger.debug(f"[{analyst_name}] 🔍 内容类型: {type(content)}")
                    logger.debug(f"[{analyst_name}] 🔍 内容长度: {len(content) if content else 0}")
                    logger.debug(f"[{analyst_name}] 🔍 内容是否为空: {not content}")
                    
                    if content:
                        content_preview = content[:200] + "..." if len(content) > 200 else content
                        logger.debug(f"[{analyst_name}] 🔍 内容预览: {content_preview}")
                        
                        report = content
                        logger.info(f"[{analyst_name}] ✅ Google模型最终分析报告生成成功，长度: {len(report)} 字符")
                        
                        # 返回完整的消息序列
                        all_messages = [result] + tool_messages + [final_result]
                        return report, all_messages
                    else:
                        logger.warning(f"[{analyst_name}] ⚠️ Google模型返回内容为空")
                        logger.debug(f"[{analyst_name}] 🔍 空内容详情: repr={repr(content)}")
                else:
                    logger.warning(f"[{analyst_name}] ⚠️ Google模型返回结果没有content属性")
                    logger.debug(f"[{analyst_name}] 🔍 可用属性: {[attr for attr in dir(final_result) if not attr.startswith('_')]}")
                
                # 如果到这里，说明内容为空或没有content属性
                logger.warning(f"[{analyst_name}] ⚠️ Google模型最终分析报告生成失败 - 内容为空")
                # 降级处理：基于工具结果生成简单报告
                tool_summary = "\n\n".join([f"工具结果 {i+1}:\n{str(result)}" for i, result in enumerate(tool_results)])
                report = f"{analyst_name}工具调用完成，获得以下数据：\n\n{tool_summary}"
                logger.info(f"[{analyst_name}] 🔄 使用降级报告，长度: {len(report)} 字符")
                return report, [result] + tool_messages
                
            except Exception as final_error:
                logger.error(f"[{analyst_name}] ❌ 最终分析报告生成失败: {final_error}")
                logger.error(f"[{analyst_name}] ❌ 异常类型: {type(final_error).__name__}")
                logger.error(f"[{analyst_name}] ❌ 异常详情: {str(final_error)}")
                
                # 记录详细的异常堆栈
                import traceback
                error_traceback = traceback.format_exc()
                logger.error(f"[{analyst_name}] ❌ 异常堆栈:\n{error_traceback}")
                
                # 降级处理：基于工具结果生成简单报告
                tool_summary = "\n\n".join([f"工具结果 {i+1}:\n{str(result)}" for i, result in enumerate(tool_results)])
                report = f"{analyst_name}工具调用完成，获得以下数据：\n\n{tool_summary}"
                logger.info(f"[{analyst_name}] 🔄 异常后使用降级报告，长度: {len(report)} 字符")
                return report, [result] + tool_messages
                
        except Exception as e:
            logger.error(f"[{analyst_name}] ❌ Google模型工具调用处理失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 降级处理：返回工具调用信息
            tool_names = [tc.get('name', 'unknown') for tc in result.tool_calls]
            report = f"{analyst_name}调用了工具 {tool_names} 但处理失败: {str(e)}"
            return report, [result]
    
    @staticmethod
    def _get_tool_name(tool) -> str:
        """安全地获取工具名称"""
        if hasattr(tool, 'name'):
            return tool.name
        elif hasattr(tool, '__name__'):
            return tool.__name__
        else:
            return str(tool)
    
    @staticmethod
    def handle_simple_google_response(
        result: AIMessage,
        llm: Any,
        analyst_name: str = "分析师"
    ) -> str:
        """
        处理简单的Google模型响应（无工具调用）
        
        Args:
            result: LLM调用结果
            llm: 语言模型实例
            analyst_name: 分析师名称
            
        Returns:
            str: 分析报告
        """
        
        if not GoogleToolCallHandler.is_google_model(llm):
            return result.content
        
        logger.info(f"[{analyst_name}] 📝 Google模型直接回复，长度: {len(result.content)} 字符")
        
        # 检查内容长度，如果过长进行处理
        if len(result.content) > 15000:
            logger.warning(f"[{analyst_name}] ⚠️ Google模型输出过长，进行截断处理...")
            return result.content[:10000] + "\n\n[注：内容已截断以确保可读性]"
        
        return result.content
    
    @staticmethod
    def generate_final_analysis_report(llm, messages: List, analyst_name: str) -> str:
        """
        生成最终分析报告 - 增强版，支持重试和模型切换
        
        Args:
            llm: LLM实例
            messages: 消息列表
            analyst_name: 分析师名称
            
        Returns:
            str: 分析报告
        """
        if not GoogleToolCallHandler.is_google_model(llm):
            logger.warning(f"⚠️ [{analyst_name}] 非Google模型，跳过Google工具处理器")
            return ""
        
        # 重试配置
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                logger.debug(f"🔍 [{analyst_name}] ===== 最终分析报告生成开始 (尝试 {attempt + 1}/{max_retries}) =====")
                logger.debug(f"🔍 [{analyst_name}] LLM类型: {type(llm).__name__}")
                logger.debug(f"🔍 [{analyst_name}] LLM模型: {getattr(llm, 'model', 'unknown')}")
                logger.debug(f"🔍 [{analyst_name}] 消息数量: {len(messages)}")
                
                # 记录消息类型和长度
                for i, msg in enumerate(messages):
                    msg_type = type(msg).__name__
                    if hasattr(msg, 'content'):
                        content_length = len(str(msg.content)) if msg.content else 0
                        logger.debug(f"🔍 [{analyst_name}] 消息{i+1}: {msg_type}, 长度: {content_length}")
                    else:
                        logger.debug(f"🔍 [{analyst_name}] 消息{i+1}: {msg_type}, 无content属性")
                
                # 构建分析提示 - 根据尝试次数调整
                if attempt == 0:
                    analysis_prompt = f"""
                    基于以上工具调用的结果，请为{analyst_name}生成一份详细的分析报告。
                    
                    要求：
                    1. 综合分析所有工具返回的数据
                    2. 提供清晰的投资建议和风险评估
                    3. 报告应该结构化且易于理解
                    4. 包含具体的数据支撑和分析逻辑
                    
                    请生成完整的分析报告：
                    """
                elif attempt == 1:
                    analysis_prompt = f"""
                    请简要分析{analyst_name}的工具调用结果并提供投资建议。
                    要求：简洁明了，包含关键数据和建议。
                    """
                else:
                    analysis_prompt = f"""
                    请为{analyst_name}提供一个简短的分析总结。
                    """
                
                logger.debug(f"🔍 [{analyst_name}] 分析提示预览: {analysis_prompt[:100]}...")
                
                # 优化消息序列
                optimized_messages = GoogleToolCallHandler._optimize_message_sequence(messages, analysis_prompt)
                
                logger.info(f"[{analyst_name}] 🚀 正在调用LLM.invoke() (尝试 {attempt + 1}/{max_retries})...")
                
                # 调用LLM生成报告
                import time
                start_time = time.time()
                result = llm.invoke(optimized_messages)
                end_time = time.time()
                
                logger.info(f"[{analyst_name}] ✅ LLM.invoke()调用完成 (耗时: {end_time - start_time:.2f}秒)")
                
                # 详细检查返回结果
                logger.debug(f"🔍 [{analyst_name}] 返回结果类型: {type(result).__name__}")
                logger.debug(f"🔍 [{analyst_name}] 返回结果属性: {dir(result)}")
                
                if hasattr(result, 'content'):
                    content = result.content
                    logger.debug(f"🔍 [{analyst_name}] 内容类型: {type(content)}")
                    logger.debug(f"🔍 [{analyst_name}] 内容长度: {len(content) if content else 0}")
                    
                    if not content or len(content.strip()) == 0:
                        logger.warning(f"[{analyst_name}] ⚠️ Google模型返回内容为空 (尝试 {attempt + 1}/{max_retries})")
                        
                        if attempt < max_retries - 1:
                            logger.info(f"[{analyst_name}] 🔄 等待{retry_delay}秒后重试...")
                            time.sleep(retry_delay)
                            continue
                        else:
                            logger.warning(f"[{analyst_name}] ⚠️ Google模型最终分析报告生成失败 - 所有重试均返回空内容")
                            # 使用降级报告
                            fallback_report = GoogleToolCallHandler._generate_fallback_report(messages, analyst_name)
                            logger.info(f"[{analyst_name}] 🔄 使用降级报告，长度: {len(fallback_report)} 字符")
                            return fallback_report
                    else:
                        logger.info(f"[{analyst_name}] ✅ 成功生成分析报告，长度: {len(content)} 字符")
                        return content
                else:
                    logger.error(f"[{analyst_name}] ❌ 返回结果没有content属性 (尝试 {attempt + 1}/{max_retries})")
                    
                    if attempt < max_retries - 1:
                        logger.info(f"[{analyst_name}] 🔄 等待{retry_delay}秒后重试...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        fallback_report = GoogleToolCallHandler._generate_fallback_report(messages, analyst_name)
                        logger.info(f"[{analyst_name}] 🔄 使用降级报告，长度: {len(fallback_report)} 字符")
                        return fallback_report
                        
            except Exception as e:
                logger.error(f"[{analyst_name}] ❌ LLM调用异常 (尝试 {attempt + 1}/{max_retries}): {e}")
                logger.error(f"[{analyst_name}] ❌ 异常类型: {type(e).__name__}")
                logger.error(f"[{analyst_name}] ❌ 完整异常信息:\n{traceback.format_exc()}")
                
                if attempt < max_retries - 1:
                    logger.info(f"[{analyst_name}] 🔄 等待{retry_delay}秒后重试...")
                    time.sleep(retry_delay)
                    continue
                else:
                    # 使用降级报告
                    fallback_report = GoogleToolCallHandler._generate_fallback_report(messages, analyst_name)
                    logger.info(f"[{analyst_name}] 🔄 使用降级报告，长度: {len(fallback_report)} 字符")
                    return fallback_report
        
        # 如果所有重试都失败，返回降级报告
        fallback_report = GoogleToolCallHandler._generate_fallback_report(messages, analyst_name)
        logger.info(f"[{analyst_name}] 🔄 所有重试失败，使用降级报告，长度: {len(fallback_report)} 字符")
        return fallback_report
    
    @staticmethod
    def _optimize_message_sequence(messages: List, analysis_prompt: str) -> List:
        """
        优化消息序列，确保在合理长度内
        
        Args:
            messages: 原始消息列表
            analysis_prompt: 分析提示
            
        Returns:
            List: 优化后的消息列表
        """
        from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
        
        # 计算总长度
        total_length = sum(len(str(msg.content)) for msg in messages if hasattr(msg, 'content'))
        total_length += len(analysis_prompt)
        
        if total_length <= 50000:
            # 长度合理，直接添加分析提示
            return messages + [HumanMessage(content=analysis_prompt)]
        
        # 需要优化：保留关键消息
        optimized_messages = []
        
        # 保留最后的用户消息
        for msg in messages:
            if isinstance(msg, HumanMessage):
                optimized_messages = [msg]
                break
        
        # 保留AI消息和工具消息，但截断过长内容
        for msg in messages:
            if isinstance(msg, (AIMessage, ToolMessage)):
                if hasattr(msg, 'content') and len(str(msg.content)) > 5000:
                    # 截断过长内容
                    truncated_content = str(msg.content)[:5000] + "\n\n[注：数据已截断以确保处理效率]"
                    if isinstance(msg, AIMessage):
                        optimized_msg = AIMessage(content=truncated_content)
                    else:
                        optimized_msg = ToolMessage(
                            content=truncated_content,
                            tool_call_id=getattr(msg, 'tool_call_id', 'unknown')
                        )
                    optimized_messages.append(optimized_msg)
                else:
                    optimized_messages.append(msg)
        
        # 添加分析提示
        optimized_messages.append(HumanMessage(content=analysis_prompt))
        
        return optimized_messages
    
    @staticmethod
    def _generate_fallback_report(messages: List, analyst_name: str) -> str:
        """
        生成降级报告
        
        Args:
            messages: 消息列表
            analyst_name: 分析师名称
            
        Returns:
            str: 降级报告
        """
        from langchain_core.messages import ToolMessage
        
        # 提取工具结果
        tool_results = []
        for msg in messages:
            if isinstance(msg, ToolMessage) and hasattr(msg, 'content'):
                content = str(msg.content)
                if len(content) > 1000:
                    content = content[:1000] + "\n\n[注：数据已截断]"
                tool_results.append(content)
        
        if tool_results:
            tool_summary = "\n\n".join([f"工具结果 {i+1}:\n{result}" for i, result in enumerate(tool_results)])
            report = f"{analyst_name}工具调用完成，获得以下数据：\n\n{tool_summary}\n\n注：由于模型响应异常，此为基于工具数据的简化报告。"
        else:
            report = f"{analyst_name}分析完成，但未能获取到有效的工具数据。建议检查数据源或重新尝试分析。"
        
        return report
    
    @staticmethod
    def create_analysis_prompt(
        ticker: str,
        company_name: str,
        analyst_type: str,
        specific_requirements: str = ""
    ) -> str:
        """
        创建标准的分析提示词
        
        Args:
            ticker: 股票代码
            company_name: 公司名称
            analyst_type: 分析师类型（如"技术分析"、"基本面分析"等）
            specific_requirements: 特定要求
            
        Returns:
            str: 分析提示词
        """
        
        base_prompt = f"""现在请基于上述工具获取的数据，生成详细的{analyst_type}报告。

**股票信息：**
- 公司名称：{company_name}
- 股票代码：{ticker}

**分析要求：**
1. 报告必须基于工具返回的真实数据进行分析
2. 包含具体的数值和专业分析
3. 提供明确的投资建议和风险提示
4. 报告长度不少于800字
5. 使用中文撰写
6. 确保在分析中正确使用公司名称"{company_name}"和股票代码"{ticker}"

{specific_requirements}

请生成专业、详细的{analyst_type}报告。"""
        
        return base_prompt