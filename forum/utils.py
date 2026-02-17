import markdown
import bleach

ALLOWED_TAGS = list(bleach.sanitizer.ALLOWED_TAGS) + [
    "p", "pre", "code", "img", "h1", "h2", "h3", "h4", "blockquote", "br"
]

ALLOWED_ATTRIBUTES = {
    "img": ["src", "alt"],
    "a": ["href", "title"],
}

def render_markdown(text):
    """
    Render markdown text to safe HTML.
    Supports:
    - Bold: **text**
    - Italic: *text*
    - Code: `code` or ```code block```
    - Links: [text](url)
    - Images: ![alt](url)
    - Headers: # Header
    - Blockquotes: > quote
    """
    if not text:
        return ""
    
    html = markdown.markdown(
        text,
        extensions=["fenced_code", "tables"]
    )
    return bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True
    )
