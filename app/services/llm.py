"""
LLM service — wraps Gemini (default), Anthropic, and OpenAI.
Provider selected by settings.DEFAULT_LLM_PROVIDER.
"""
from app.settings import settings


async def run_prompt(prompt: str, context: str = "") -> str:
    """
    Run a prompt against the configured LLM provider.
    context: optional personal relevance context_text to append.
    """
    full_prompt = prompt
    if context:
        full_prompt += f"\n\n---\nPersonal context (use to make the output more relevant to this specific user):\n{context}"

    provider = settings.DEFAULT_LLM_PROVIDER

    if provider == "gemini":
        return await _run_gemini(full_prompt)
    elif provider == "anthropic":
        return await _run_anthropic(full_prompt)
    elif provider == "openai":
        return await _run_openai(full_prompt)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


async def _run_gemini(prompt: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text


async def _run_anthropic(prompt: str) -> str:
    import anthropic
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
    message = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


async def _run_openai(prompt: str) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
