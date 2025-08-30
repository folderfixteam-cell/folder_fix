from django import template
import re

register = template.Library()

@register.filter
def highlight(text):
    """
    Replace **text** with <span class='highlight'>text</span>
    """
    if not text:
        return ""
    # Regex to replace **word** with span
    return re.sub(r'\*\*(.*?)\*\*', r"<span class='mark'>\1</span>", text)
