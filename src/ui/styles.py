# -*- coding: utf-8 -*-
"""
UI 样式定义 - 保留用于向后兼容
"""

# 自定义 CSS 样式
CUSTOM_CSS = """
.gradio-container {
    max-width: 1480px !important;
}
.mv-image button .wrap {
    font-size: 10px;
}
.mv-image .icon-wrap {
    width: 20px;
}
"""

# 标题 HTML
TITLE_HTML = """
<div style="font-size: 2em; font-weight: bold; text-align: center; margin-bottom: 5px">
🎨 Hunyuan3D Shape Generation
</div>
<div style="text-align: center; color: #666; margin-bottom: 10px;">
高质量图像转 3D 模型生成服务 | 支持单图和多视图输入
</div>
"""

# 页脚 HTML
FOOTER_HTML = """
<div style="text-align: center; padding: 20px; color: #9ca3af; font-size: 12px;">
    <p>Powered by Tencent Hunyuan3D | Built with Gradio</p>
</div>
"""
