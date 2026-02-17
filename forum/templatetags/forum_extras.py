from django import template
from forum.utils import render_markdown

register = template.Library()

@register.filter
def render_md(text):
    """Filter to render markdown content to safe HTML"""
    return render_markdown(text)
