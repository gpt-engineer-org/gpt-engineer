import json

from typing import Dict, Optional


class Prompt:
    def __init__(
        self,
        text: str,
        image_urls: Optional[Dict[str, str]] = None,
        entrypoint_prompt: str = "",
        prefix: Optional[str] = "Request: ",
    ):
        self.text = text
        self.image_urls = image_urls
        self.entrypoint_prompt = entrypoint_prompt
        self.prefix = prefix

    def __repr__(self):
        return f"Prompt(text={self.text!r}, image_urls={self.image_urls!r})"

    def to_langchain_content(self) -> Dict[str, str]:
        content = [{"type": "text", "text": f"{self.prefix}{self.text}"}]

        if self.image_urls:
            for name, url in self.image_urls.items():
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": url,
                        "detail": "low",
                    },
                }
                content.append(image_content)

        return content

    def to_dict(self):
        return {
            "text": self.text,
            "image_urls": self.image_urls,
            "entrypoint_prompt": self.entrypoint_prompt,
        }

    def to_json(self):
        return json.dumps(self.to_dict())
