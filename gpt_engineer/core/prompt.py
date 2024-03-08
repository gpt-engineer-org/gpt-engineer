from typing import Optional, Dict, Union
from pathlib import Path

class Prompt:
    def __init__(self, text: str, image_urls: Optional[Dict[str, str]] = None):
        self.text = text
        self.image_urls = image_urls

    def __repr__(self):
        return f"Prompt(text={self.text!r}, image_urls={self.image_urls!r})"
    
    def to_langchain_content(self):
        content = [
            {"type": "text", "text": f"Request: {self.text}"}
        ]
        
        if (self.image_urls):
            for name, url in self.image_urls.items():
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": url,
                        "detail": 'low',
                    }
                }
                content.append(image_content)
        
        return content