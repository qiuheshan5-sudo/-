"""
公众号文章检测器 — FastAPI 后端
"""

from pathlib import Path

from dotenv import load_dotenv

# 加载项目根目录的 .env
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from analyzer import analyze_article

app = FastAPI(title="公众号文章检测器")

# 静态文件
static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


class ArticleRequest(BaseModel):
    title: str = ""
    content: str


@app.get("/")
async def index():
    return FileResponse(static_dir / "index.html")


@app.post("/api/analyze")
async def api_analyze(req: ArticleRequest):
    if not req.content.strip():
        return {"error": "请输入文章内容"}

    title = req.title.strip() or "（无标题）"
    content = req.content.strip()

    # 截断过长文本（TypeSafe token 限制）
    if len(content) > 8000:
        content = content[:8000] + "…（已截断）"

    result = await analyze_article(title, content)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8899)
