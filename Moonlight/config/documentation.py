from markdown2 import markdown

import aiofiles

async def read_docs(docs_path: str) -> str:
    async with aiofiles.open(docs_path, 'r', encoding='utf-8') as documentation:
        content: str = await documentation.read()

        return f'''
            <div style="text-align: center;">
                {markdown(content)}
            </div>
        '''