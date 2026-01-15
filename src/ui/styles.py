# -*- coding: utf-8 -*-
"""
UI 样式定义
"""

# 自定义 CSS 样式
CUSTOM_CSS = """
/* 全局样式 */
.gradio-container {
    max-width: 1400px !important;
    margin: auto !important;
}

/* 标题样式 */
.title-container {
    text-align: center;
    padding: 20px 0;
    margin-bottom: 20px;
}

.title-container h1 {
    font-size: 2.2em;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}

.title-container p {
    color: #6b7280;
    font-size: 1.1em;
}

/* 输入图像样式 */
.input-image {
    border-radius: 12px !important;
    overflow: hidden;
}

/* 多视图图像样式 */
.mv-image {
    border-radius: 8px !important;
}

.mv-image button .wrap {
    font-size: 11px;
}

.mv-image .icon-wrap {
    width: 18px;
}

.mv-front {
    border: 2px solid #3b82f6 !important;
}

/* 模型查看器容器 */
.model-viewer-container {
    border-radius: 12px;
    overflow: hidden;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 按钮样式 */
.generate-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    transition: transform 0.2s, box-shadow 0.2s !important;
}

.generate-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
}

.generate-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

/* 状态指示器 */
.status-indicator {
    margin-bottom: 16px;
}

/* Tab 样式 */
.tabs {
    border-radius: 12px;
    overflow: hidden;
}

/* Accordion 样式 */
.accordion {
    border-radius: 8px !important;
    margin-bottom: 12px !important;
}

/* 滑块样式 */
input[type="range"] {
    accent-color: #667eea;
}

/* 文件下载按钮 */
.download-btn {
    background: #10b981 !important;
    border: none !important;
}

.download-btn:hover {
    background: #059669 !important;
}

/* 统计信息面板 */
.stats-panel {
    background: #f8fafc;
    border-radius: 8px;
    padding: 16px;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .gradio-container {
        padding: 10px !important;
    }
    
    .title-container h1 {
        font-size: 1.6em;
    }
}

/* 加载动画 */
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.loading {
    animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
"""

# 标题 HTML
TITLE_HTML = """
<div class="title-container">
    <h1>🎨 Hunyuan3D Shape Generation</h1>
    <p>高质量图像转 3D 模型生成服务 | 支持单图和多视图输入</p>
</div>
"""

# 页脚 HTML
FOOTER_HTML = """
<div style="text-align: center; padding: 20px; color: #9ca3af; font-size: 12px;">
    <p>Powered by Tencent Hunyuan3D | Built with Gradio</p>
</div>
"""
