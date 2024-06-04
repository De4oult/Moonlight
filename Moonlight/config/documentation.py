from markdown.extensions.fenced_code import FencedCodeExtension
from markdown                        import markdown

import aiofiles

async def read_docs(docs_path: str) -> str:
    async with aiofiles.open(docs_path, 'r', encoding='utf-8') as documentation:
        content: str = await documentation.read()

        return markdown(content, extensions = [FencedCodeExtension()])