"""One entry point for LLM steps. Runs as a CrewAI agent when USE_CREWAI=true, else calls Groq directly.
If a model has been retired (Groq retires models regularly), it automatically tries FALLBACK_MODELS."""
from __future__ import annotations

import re

import config

_DEAD: set[str] = set()  # models that returned "not found" this run


def available() -> bool:
    return bool(config.GROQ_API_KEY)


def _clean(text: str | None) -> str:
    return re.sub(r"<think>.*?</think>", "", text or "", flags=re.S).strip()


def _call(system: str, prompt: str, model: str, max_tokens: int) -> str:
    from groq import Groq

    kwargs = {}
    if model.startswith("openai/gpt-oss"):
        kwargs["extra_body"] = {"reasoning_effort": "low"}  # keep thinking short on the free tier
        max_tokens *= 3  # reasoning tokens count against the limit
    resp = Groq(api_key=config.GROQ_API_KEY).chat.completions.create(
        model=model,
        temperature=0.2,
        max_tokens=max_tokens,
        messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
        **kwargs,
    )
    return _clean(resp.choices[0].message.content)


def _is_model_error(exc: Exception) -> bool:
    return getattr(exc, "status_code", None) in (400, 404) and "model" in str(exc).lower()


def _direct(system: str, prompt: str, model: str, max_tokens: int) -> str:
    tried, last = [], None
    for m in dict.fromkeys([model, *config.FALLBACK_MODELS]):
        if m in _DEAD:
            continue
        tried.append(m)
        try:
            out = _call(system, prompt, m, max_tokens)
            if out:
                return out
            last = RuntimeError(f"{m} returned an empty answer")
        except Exception as exc:
            if _is_model_error(exc):
                _DEAD.add(m)
                last = exc
                continue
            raise
    raise RuntimeError(f"No working Groq model (tried {', '.join(tried) or 'none'}). Update FAST_MODEL/SMART_MODEL in settings.env. Last error: {last}")


def _crew(role: str, goal: str, backstory: str, prompt: str, model: str) -> str:
    from crewai import Agent, Crew, LLM, Process, Task

    llm = LLM(model=f"groq/{model}", api_key=config.GROQ_API_KEY, temperature=0.2)
    agent = Agent(role=role, goal=goal, backstory=backstory, llm=llm, allow_delegation=False, verbose=False)
    task = Task(description=prompt, expected_output="Only the final answer, nothing else.", agent=agent)
    result = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False).kickoff()
    return _clean(getattr(result, "raw", None) or str(result))


def run_agent(role: str, goal: str, backstory: str, prompt: str, model: str, max_tokens: int = 700) -> str:
    if config.USE_CREWAI:
        try:
            return _crew(role, goal, backstory, prompt, model)
        except Exception:
            pass  # crewai missing or model problem: fall back to the direct, self-healing path
    return _direct(f"You are the {role}. {backstory} Goal: {goal}", prompt, model, max_tokens)
