"\"\"
公众号文章检测器 — FastAPI 后端 (单文件版)
\"\"\"

from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from analyzer import analyze_article

app = FastAPI(title="公众号文章检测器")

HTML_CONTENT = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>公众号文章检测器</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
        body { font-family: 'Noto Sans SC', sans-serif; }
        .bar-fill { transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); }
        .score-fill { transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1); }
        .fade-in { animation: fadeIn 0.5s ease-out; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        textarea:focus { outline: none; box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.5); }
    </style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen">

    <!-- Header -->
    <header class="border-b border-gray-800 bg-gray-950/80 backdrop-blur sticky top-0 z-10">
        <div class="max-w-6xl mx-auto px-6 py-4 flex items-center gap-3">
            <span class="text-2xl">🔍</span>
            <h1 class="text-xl font-bold">公众号文章检测器</h1>
            <span class="text-sm text-gray-500 ml-2">Powered by TypeSafe System One</span>
        </div>
    </header>

    <main class="max-w-6xl mx-auto px-6 py-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">

            <!-- Left: Input -->
            <div class="space-y-4">
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-2">文章标题</label>
                    <input id="titleInput" type="text" placeholder="粘贴文章标题（可选）"
                        class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-600 focus:border-indigo-500 transition">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-400 mb-2">文章正文</label>
                    <textarea id="contentInput" rows="20" placeholder="粘贴公众号文章正文..."
                        class="w-full bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-600 resize-y focus:border-indigo-500 transition"></textarea>
                </div>
                <div class="flex items-center gap-4">
                    <button id="analyzeBtn" onclick="analyze()"
                        class="bg-indigo-600 hover:bg-indigo-500 text-white font-medium px-8 py-3 rounded-lg transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
                        <span id="btnText">开始检测</span>
                        <span id="btnSpinner" class="hidden">
                            <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/></svg>
                        </span>
                    </button>
                    <span id="charCount" class="text-sm text-gray-500"></span>
                </div>
            </div>

            <!-- Right: Results -->
            <div id="resultPanel" class="space-y-6">
                <!-- Placeholder -->
                <div id="placeholder" class="flex flex-col items-center justify-center h-96 text-gray-600">
                    <span class="text-6xl mb-4">📝</span>
                    <p>粘贴文章，点击检测</p>
                    <p class="text-sm mt-1">一次调用，11 个维度分析</p>
                </div>

                <!-- Verdict -->
                <div id="verdictCard" class="hidden fade-in bg-gray-900 border border-gray-700 rounded-xl p-6">
                    <div id="verdictText" class="text-2xl font-bold text-center"></div>
                    <div id="verdictSub" class="text-center text-gray-400 mt-2 text-sm"></div>
                </div>

                <!-- Category & Style -->
                <div id="classifyCard" class="hidden fade-in grid grid-cols-2 gap-4">
                    <div class="bg-gray-900 border border-gray-700 rounded-xl p-5">
                        <div class="text-xs text-gray-500 uppercase tracking-wider mb-2">文章类型</div>
                        <div id="categoryLabel" class="text-lg font-bold"></div>
                        <div id="categoryConf" class="text-sm text-gray-400 mt-1"></div>
                        <div id="categoryDist" class="mt-3 space-y-1"></div>
                    </div>
                    <div class="bg-gray-900 border border-gray-700 rounded-xl p-5">
                        <div class="text-xs text-gray-500 uppercase tracking-wider mb-2">写作风格</div>
                        <div id="styleLabel" class="text-lg font-bold"></div>
                        <div id="styleConf" class="text-sm text-gray-400 mt-1"></div>
                    </div>
                </div>

                <!-- Scores -->
                <div id="scoresCard" class="hidden fade-in bg-gray-900 border border-gray-700 rounded-xl p-5 space-y-5">
                    <div class="text-xs text-gray-500 uppercase tracking-wider">评分维度</div>
                    <div id="scoresContainer" class="space-y-4"></div>
                </div>

                <!-- Checks -->
                <div id="checksCard" class="hidden fade-in bg-gray-900 border border-gray-700 rounded-xl p-5 space-y-4">
                    <div class="text-xs text-gray-500 uppercase tracking-wider">多维检测</div>
                    <div id="checksContainer" class="space-y-3"></div>
                </div>

                <!-- Suggestions -->
                <div id="suggestionsCard" class="hidden fade-in bg-gray-900 border border-indigo-800 rounded-xl p-5 space-y-4">
                    <div class="text-xs text-indigo-400 uppercase tracking-wider font-medium">💡 改进方案</div>
                    <div id="suggestionsContainer" class="space-y-3"></div>
                </div>

                <!-- Usage -->
                <div id="usageCard" class="hidden fade-in text-center text-xs text-gray-600 py-2">
                </div>
            </div>
        </div>
    </main>

    <script>
    const contentInput = document.getElementById('contentInput');
    const charCount = document.getElementById('charCount');

    contentInput.addEventListener('input', () => {
        const len = contentInput.value.length;
        charCount.textContent = len > 0 ? `${len} 字` : '';
    });

    async function analyze() {
        const title = document.getElementById('titleInput').value;
        const content = contentInput.value;

        if (!content.trim()) {
            alert('请粘贴文章内容');
            return;
        }

        const btn = document.getElementById('analyzeBtn');
        const btnText = document.getElementById('btnText');
        const spinner = document.getElementById('btnSpinner');

        btn.disabled = true;
        btnText.textContent = '检测中...';
        spinner.classList.remove('hidden');

        // Hide placeholder
        document.getElementById('placeholder').classList.add('hidden');

        try {
            const resp = await fetch('/api/analyze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title, content }),
            });
            const data = await resp.json();

            if (data.error) {
                alert(data.error);
                return;
            }

            renderResults(data);
        } catch (e) {
            alert('请求失败: ' + e.message);
        } finally {
            btn.disabled = false;
            btnText.textContent = '重新检测';
            spinner.classList.add('hidden');
        }
    }

    function renderResults(data) {
        // Verdict
        const verdictCard = document.getElementById('verdictCard');
        verdictCard.classList.remove('hidden');
        document.getElementById('verdictText').textContent = data.verdict;
        document.getElementById('verdictSub').textContent =
            `传播潜力 ${Math.round(data.viral_score * 100)}%`;

        // Category & Style
        document.getElementById('classifyCard').classList.remove('hidden');
        document.getElementById('categoryLabel').textContent =
            `${data.category.label}`;
        document.getElementById('categoryConf').textContent =
            `置信度 ${Math.round(data.category.confidence * 100)}%`;

        const distEl = document.getElementById('categoryDist');
        distEl.innerHTML = '';
        for (const [label, prob] of Object.entries(data.category.probabilities)) {
            if (prob < 0.01) continue;
            distEl.innerHTML += `
                <div class="flex items-center gap-2 text-xs">
                    <span class="w-12 text-gray-400 text-right">${label}</span>
                    <div class="flex-1 bg-gray-800 rounded-full h-2">
                        <div class="bar-fill bg-indigo-500 h-2 rounded-full" style="width: 0%" data-width="${prob * 100}%"></div>
                    </div>
                    <span class="w-10 text-gray-500">${Math.round(prob * 100)}%</span>
                </div>`;
        }

        document.getElementById('styleLabel').textContent = data.writing_style.label;
        document.getElementById('styleConf').textContent =
            `置信度 ${Math.round(data.writing_style.confidence * 100)}%`;

        // Scores
        document.getElementById('scoresCard').classList.remove('hidden');
        const scoresContainer = document.getElementById('scoresContainer');
        scoresContainer.innerHTML = '';

        const scoreLabels = {
            emotional_tone: { name: '情绪基调', emoji: '🎭' },
            depth: { name: '思想深度', emoji: '🧠' },
            readability: { name: '可读性', emoji: '📖' },
        };

        for (const [key, info] of Object.entries(scoreLabels)) {
            const s = data.scores[key];
            const pct = (s.value / s.max) * 100;
            scoresContainer.innerHTML += `
                <div>
                    <div class="flex justify-between items-center mb-1">
                        <span class="text-sm">${info.emoji} ${info.name}</span>
                        <span class="text-sm text-gray-400">${s.label} · ${s.value}/${s.max}</span>
                    </div>
                    <div class="bg-gray-800 rounded-full h-3">
                        <div class="score-fill h-3 rounded-full ${pct >= 60 ? 'bg-emerald-500' : pct >= 30 ? 'bg-amber-500' : 'bg-red-500'}"
                            style="width: 0%" data-width="${pct}%"></div>
                    </div>
                </div>`;
        }

        // Checks
        document.getElementById('checksCard').classList.remove('hidden');
        const checksContainer = document.getElementById('checksContainer');
        checksContainer.innerHTML = '';

        for (const [key, check] of Object.entries(data.checks)) {
            const pct = check.value * 100;
            const isWarning = check.warning && pct > 50;
            const barColor = check.warning
                ? (pct > 70 ? 'bg-red-500' : pct > 40 ? 'bg-amber-500' : 'bg-emerald-500')
                : (pct > 60 ? 'bg-emerald-500' : pct > 30 ? 'bg-amber-500' : 'bg-gray-600');

            checksContainer.innerHTML += `
                <div class="flex items-center gap-3">
                    <span class="text-lg w-7">${check.emoji}</span>
                    <span class="text-sm w-20 ${isWarning ? 'text-red-400 font-medium' : 'text-gray-300'}">${check.label}</span>
                    <div class="flex-1 bg-gray-800 rounded-full h-2.5">
                        <div class="bar-fill ${barColor} h-2.5 rounded-full" style="width: 0%" data-width="${pct}%"></div>
                    </div>
                    <span class="text-sm w-12 text-right ${isWarning ? 'text-red-400' : 'text-gray-400'}">${Math.round(pct)}%</span>
                </div>`;
        }

        // Suggestions
        if (data.suggestions && data.suggestions.length > 0) {
            document.getElementById('suggestionsCard').classList.remove('hidden');
            const sugContainer = document.getElementById('suggestionsContainer');
            sugContainer.innerHTML = '';
            
            data.suggestions.forEach(sug => {
                const badgeColor = sug.priority === 'high' ? 'bg-red-500/20 text-red-400 border-red-500/30' : 
                                   sug.priority === 'medium' ? 'bg-amber-500/20 text-amber-400 border-amber-500/30' :
                                   sug.priority === 'low' ? 'bg-blue-500/20 text-blue-400 border-blue-500/30' :
                                   'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
                
                sugContainer.innerHTML += `
                    <div class="bg-gray-800/50 rounded-lg p-3 border border-gray-700/50">
                        <div class="flex items-center gap-2 mb-1.5">
                            <span class="font-medium text-gray-200">${sug.area}</span>
                            <span class="text-[10px] px-1.5 py-0.5 rounded border ${badgeColor}">${sug.priority.toUpperCase()}</span>
                        </div>
                        <p class="text-sm text-gray-400 leading-relaxed">${sug.detail}</p>
                    </div>
                `;
            });
        }

        // Usage
        const usageCard = document.getElementById('usageCard');
        usageCard.classList.remove('hidden');
        usageCard.textContent = `Token 用量: 输入 ${data.usage.input_tokens} · 输出 ${data.usage.output_tokens}`;

        // Animate bars
        requestAnimationFrame(() => {
            setTimeout(() => {
                document.querySelectorAll('[data-width]').forEach(el => {
                    el.style.width = el.dataset.width;
                });
            }, 100);
        });
    }
    </script>
</body>
</html>

"""

class ArticleRequest(BaseModel):
    title: str = ""
    content: str

@app.head("/")
@app.get("/")
async def index():
    return HTMLResponse(content=HTML_CONTENT)

@app.post("/api/analyze")
async def api_analyze(req: ArticleRequest):
    if not req.content.strip():
        return {"error": "请输入文章内容"}

    title = req.title.strip() or "（无标题）"
    content = req.content.strip()

    if len(content) > 8000:
        content = content[:8000] + "…（已截断）"

    result = await analyze_article(title, content)
    return result
