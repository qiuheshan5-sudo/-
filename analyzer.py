"""
TypeSafe 文章分析引擎
一次 API 调用完成 11 个维度的文章检测
"""

from typesafe_sdk import AsyncTypeSafeClient, Choice, Noul, Score


async def analyze_article(title: str, content: str) -> dict:
    """分析公众号文章，返回结构化检测结果"""

    state = {
        "title": title,
        "article": content,
        "source_type": "微信公众号文章",
    }

    async with AsyncTypeSafeClient() as client:
        response = await client.system_one(
            state=state,
            questions={
                # ── Choice ──
                "category": Choice(
                    instructions="What is the primary topic category of this WeChat article?",
                    criteria={
                        "emotion": "Relationships, love, personal feelings, life reflections",
                        "career": "Workplace, career growth, job market, professional advice",
                        "tech": "Technology, internet, digital products, AI",
                        "society": "Social issues, current events, generational trends",
                        "finance": "Money, investment, real estate, economics",
                        "health": "Physical or mental health, wellness, medical topics",
                        "education": "Learning, parenting, school, academic topics",
                    },
                ),
                "writing_style": Choice(
                    instructions="What is the dominant writing style of this article?",
                    criteria={
                        "narrative": "Story-driven, uses personal anecdotes and scenes",
                        "analytical": "Logical reasoning, structured arguments with evidence",
                        "conversational": "Casual, like chatting with a friend",
                        "emotional": "Emotionally charged, designed to provoke strong feelings",
                        "practical": "Actionable how-to, lists, tips, tutorials",
                    },
                ),
                # ── Score ──
                "emotional_tone": Score(
                    instructions="The overall emotional tone of this article",
                    criteria=[
                        "Very heavy, anxious, or pessimistic",
                        "Somewhat negative, somber",
                        "Balanced, names problems but offers perspective",
                        "Warm, encouraging, gently hopeful",
                        "Very uplifting, energizing, optimistic",
                    ],
                ),
                "depth": Score(
                    instructions="How intellectually deep and thought-provoking is this article?",
                    criteria=[
                        "Surface-level, obvious observations, cliché",
                        "Some insight but mostly common wisdom",
                        "Genuine insight with original framing",
                        "Deep, multi-layered analysis that reframes thinking",
                        "Profoundly original, paradigm-shifting",
                    ],
                ),
                "readability": Score(
                    instructions="How easy and enjoyable is this article to read?",
                    criteria=[
                        "Very hard to follow, confusing structure",
                        "Somewhat dense, requires effort",
                        "Average, competent writing",
                        "Smooth, well-paced, pleasant to read",
                        "Exceptional flow, effortless and engaging",
                    ],
                ),
                # ── Noul ──
                "viral_potential": Noul(
                    instructions="Would this article likely resonate widely and get shared on Chinese social media (WeChat Moments, Weibo)?",
                ),
                "is_clickbait": Noul(
                    instructions="Does the title use clickbait techniques: exaggeration, misleading claims, emotional manipulation, or curiosity gaps that the content doesn't deliver on?",
                ),
                "has_ad": Noul(
                    instructions="Does this article contain hidden advertising, product placement, affiliate marketing, or sponsored content disguised as editorial?",
                ),
                "targets_anxiety": Noul(
                    instructions="Does this article deliberately exploit reader anxiety about falling behind, peer comparison, or fear of missing out to manipulate emotions?",
                ),
                "is_original": Noul(
                    instructions="Does this article offer genuinely original thinking, unique perspectives, or novel insights rather than recycling common ideas?",
                ),
                "needs_fact_check": Noul(
                    instructions="Does this article make specific factual claims, cite statistics, or reference events that should be independently verified?",
                ),
                # ── 改进诊断 ──
                "title_quality": Score(
                    instructions="How compelling and effective is the article title at attracting readers while accurately representing the content?",
                    criteria=[
                        "Weak, vague, or misleading title",
                        "Generic, forgettable title",
                        "Decent title that hints at the content",
                        "Strong title that creates curiosity and delivers",
                        "Exceptional, perfectly captures the essence and hooks",
                    ],
                ),
                "has_strong_hook": Noul(
                    instructions="Does the article opening (first 2-3 paragraphs) immediately grab attention with a compelling hook — a vivid scene, surprising fact, provocative question, or relatable story?",
                ),
                "has_clear_structure": Noul(
                    instructions="Does this article have a clear logical structure with smooth transitions between sections, a coherent argument flow, and a satisfying conclusion?",
                ),
                "could_be_shorter": Noul(
                    instructions="Does this article contain unnecessary repetition, filler content, or padding that could be cut without losing meaning?",
                ),
            },
        )

    # ── 整理结果 ──
    answers = response.answers

    category_labels = {
        "emotion": "情感",
        "career": "职场",
        "tech": "科技",
        "society": "社会",
        "finance": "财经",
        "health": "健康",
        "education": "教育",
    }

    style_labels = {
        "narrative": "叙事型",
        "analytical": "说理型",
        "conversational": "对话型",
        "emotional": "煽情型",
        "practical": "干货型",
    }

    tone_labels = ["焦虑沉重", "偏消极", "平衡理性", "温暖鼓励", "积极振奋"]
    depth_labels = ["表面鸡汤", "常见道理", "有洞见", "深度思考", "开创性"]
    readability_labels = ["晦涩难懂", "略显费力", "中规中矩", "流畅好读", "极致顺滑"]

    cat = answers["category"]
    sty = answers["writing_style"]

    # 生成一句话总结
    viral = answers["viral_potential"].noul
    if viral >= 0.8:
        verdict = "🔥 这篇很有爆款潜质"
    elif viral >= 0.5:
        verdict = "👍 有一定传播力，但不一定能大火"
    else:
        verdict = "😐 传播潜力有限"

    # ── 生成改进建议 ──
    suggestions = []

    # 标题
    title_score = answers["title_quality"].score
    if title_score < 2:
        suggestions.append({
            "area": "📌 标题优化",
            "priority": "high",
            "detail": "标题吸引力不足，建议：用具体场景替代抽象概念，加入数字或对比，制造好奇心缺口。例如把「论努力的意义」改成「我见过最努力的人，后来都怎样了」。",
        })
    elif title_score < 3:
        suggestions.append({
            "area": "📌 标题微调",
            "priority": "medium",
            "detail": "标题中规中矩，可以考虑加入情感钩子或悬念感，让人更想点开。",
        })

    # 开头
    hook = answers["has_strong_hook"].noul
    if hook < 0.4:
        suggestions.append({
            "area": "🎣 开头钩子",
            "priority": "high",
            "detail": "开头缺乏吸引力。前 3 句话决定读者会不会继续看。建议：开篇直接抛出一个让人意外的故事、数据或问题，而不是铺垫背景。",
        })
    elif hook < 0.7:
        suggestions.append({
            "area": "🎣 开头钩子",
            "priority": "medium",
            "detail": "开头有一定吸引力但还可以更强。试试把最戳人的那句话提到第一段。",
        })

    # 结构
    structure = answers["has_clear_structure"].noul
    if structure < 0.4:
        suggestions.append({
            "area": "🏗️ 文章结构",
            "priority": "high",
            "detail": "文章结构较散，读者容易迷失。建议：明确「提出问题→分析原因→给出出路」的三段式，段落之间加过渡句，让论点层层递进。",
        })
    elif structure < 0.7:
        suggestions.append({
            "area": "🏗️ 文章结构",
            "priority": "medium",
            "detail": "结构基本清晰，但部分段落之间的过渡可以更顺滑，试试用「但是」「于是」「所以」等连接词引导读者。",
        })

    # 冗余
    shorter = answers["could_be_shorter"].noul
    if shorter > 0.7:
        suggestions.append({
            "area": "✂️ 精简内容",
            "priority": "high",
            "detail": "文章存在较多冗余。公众号最佳阅读长度约 1500-2500 字。建议：砍掉重复论述的段落，合并相似的例子，每个观点只用最有力的一个论据。",
        })
    elif shorter > 0.4:
        suggestions.append({
            "area": "✂️ 适当精简",
            "priority": "low",
            "detail": "部分段落可以更简练。读一遍，把每段删掉一句试试，如果意思没变就真的多余了。",
        })

    # 深度
    depth_val = answers["depth"].score
    if depth_val < 1.5:
        suggestions.append({
            "area": "🧠 思想深度",
            "priority": "high",
            "detail": "观点偏表面，容易被读者一划而过。建议：加入反直觉的洞见、反面论证、或独特的个人经历。问自己「这个道理别人说过吗？」，如果说过，换个角度再想想。",
        })
    elif depth_val < 2.5:
        suggestions.append({
            "area": "🧠 思想深度",
            "priority": "medium",
            "detail": "有一定洞见但可以更深。试试在核心观点上追问一层「为什么」——读者最爱转发的是他们「想说但说不出来」的话。",
        })

    # 情绪
    tone_val = answers["emotional_tone"].score
    anxiety = answers["targets_anxiety"].noul
    if tone_val < 1 and anxiety > 0.6:
        suggestions.append({
            "area": "🎭 情绪平衡",
            "priority": "medium",
            "detail": "文章整体偏焦虑，且有贩卖焦虑倾向。适度的焦虑能引起共鸣，但如果只有「扎刀」没有「药方」，读者会反感。建议：后半部分给出正向出路或行动方案。",
        })
    elif tone_val > 3.5:
        suggestions.append({
            "area": "🎭 情绪平衡",
            "priority": "low",
            "detail": "文章偏鸡汤，可能缺乏说服力。适当加入真实的困境和挣扎，让乐观有根基而不是空中楼阁。",
        })

    # 原创性
    original = answers["is_original"].noul
    if original < 0.3:
        suggestions.append({
            "area": "💡 原创性",
            "priority": "high",
            "detail": "观点缺乏新意，容易淹没在同类文章中。建议：加入独家故事、独特数据、或把两个看似无关的领域做类比。最好的原创不是说新话，是用新方式说旧话。",
        })

    # 可读性
    read_val = answers["readability"].score
    if read_val < 1.5:
        suggestions.append({
            "area": "📖 可读性",
            "priority": "high",
            "detail": "阅读体验需要提升。建议：缩短段落（每段不超过 4 行），多用短句，加入小标题分隔，用具体故事代替抽象论述。",
        })

    # 传播力
    viral = answers["viral_potential"].noul
    if viral < 0.5:
        suggestions.append({
            "area": "📣 传播力",
            "priority": "medium",
            "detail": "传播潜力不足。爆款公众号文章通常满足至少一个条件：引起强烈共鸣、提供社交货币、触发身份认同。检查文章是否让读者有「这说的就是我」或「我要转给 XX 看」的冲动。",
        })

    # 如果没有任何建议，说明文章已经很好了
    if not suggestions:
        suggestions.append({
            "area": "✨ 整体评价",
            "priority": "none",
            "detail": "这篇文章各方面表现都不错，继续保持！如果要精益求精，可以找几个目标读者先看一遍，收集真实反馈。",
        })

    # 按优先级排序
    priority_order = {"high": 0, "medium": 1, "low": 2, "none": 3}
    suggestions.sort(key=lambda x: priority_order.get(x["priority"], 9))

    return {
        "verdict": verdict,
        "viral_score": viral,
        "category": {
            "value": cat.choice,
            "label": category_labels.get(cat.choice, cat.choice),
            "confidence": cat.confidence,
            "probabilities": {
                category_labels.get(k, k): round(v, 2)
                for k, v in sorted(cat.probabilities.items(), key=lambda x: x[1], reverse=True)
            },
        },
        "writing_style": {
            "value": sty.choice,
            "label": style_labels.get(sty.choice, sty.choice),
            "confidence": sty.confidence,
        },
        "scores": {
            "emotional_tone": {
                "value": round(answers["emotional_tone"].score, 1),
                "max": 4,
                "label": tone_labels[round(answers["emotional_tone"].score)],
                "confidence": answers["emotional_tone"].confidence,
            },
            "depth": {
                "value": round(answers["depth"].score, 1),
                "max": 4,
                "label": depth_labels[round(answers["depth"].score)],
                "confidence": answers["depth"].confidence,
            },
            "readability": {
                "value": round(answers["readability"].score, 1),
                "max": 4,
                "label": readability_labels[round(answers["readability"].score)],
                "confidence": answers["readability"].confidence,
            },
            "title_quality": {
                "value": round(answers["title_quality"].score, 1),
                "max": 4,
                "label": ["弱", "一般", "尚可", "好", "极佳"][round(answers["title_quality"].score)],
                "confidence": answers["title_quality"].confidence,
            },
        },
        "checks": {
            "viral_potential": {
                "label": "传播潜力",
                "emoji": "🔥",
                "value": round(answers["viral_potential"].noul, 2),
            },
            "is_clickbait": {
                "label": "标题党",
                "emoji": "🎣",
                "value": round(answers["is_clickbait"].noul, 2),
                "warning": True,
            },
            "has_ad": {
                "label": "软广植入",
                "emoji": "💰",
                "value": round(answers["has_ad"].noul, 2),
                "warning": True,
            },
            "targets_anxiety": {
                "label": "贩卖焦虑",
                "emoji": "😰",
                "value": round(answers["targets_anxiety"].noul, 2),
                "warning": True,
            },
            "is_original": {
                "label": "原创性",
                "emoji": "💡",
                "value": round(answers["is_original"].noul, 2),
            },
            "needs_fact_check": {
                "label": "需要核查",
                "emoji": "⚠️",
                "value": round(answers["needs_fact_check"].noul, 2),
                "warning": True,
            },
            "has_strong_hook": {
                "label": "开头吸引力",
                "emoji": "🪝",
                "value": round(answers["has_strong_hook"].noul, 2),
            },
            "has_clear_structure": {
                "label": "结构清晰度",
                "emoji": "🏗️",
                "value": round(answers["has_clear_structure"].noul, 2),
            },
            "could_be_shorter": {
                "label": "内容冗余",
                "emoji": "✂️",
                "value": round(answers["could_be_shorter"].noul, 2),
                "warning": True,
            },
        },
        "suggestions": suggestions,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        },
    }
