import os
import json
import operator
from dataclasses import dataclass, field
from typing_extensions import TypedDict, Annotated
import warnings
import requests
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from tavily import TavilyClient

warnings.filterwarnings("ignore")



llm = ChatOllama(model=os.getenv("LOCAL_LLM_MODEL"), temperature=0)
llm_json_mode = ChatOllama(model=os.getenv("LOCAL_LLM_MODEL"), temperature=0, format="json")
tavily_client = TavilyClient(api_key=os.getenv("APIKEY"))

def deduplicate_and_format_sources(search_response, max_tokens_per_source, include_raw_content=True):
    sources_list = search_response['results'] if isinstance(search_response, dict) else []
    unique_sources = {s['url']: s for s in sources_list}
    formatted_text = "Sources:\n\n"
    for source in unique_sources.values():
        formatted_text += f"Source {source['title']}:\n===\n"
        formatted_text += f"URL: {source['url']}\n===\n"
        formatted_text += f"Most relevant content: {source['content']}\n===\n"
        if include_raw_content:
            raw = source.get('raw_content') or ''
            char_limit = max_tokens_per_source * 4
            if len(raw) > char_limit:
                raw = raw[:char_limit] + "... [truncated]"
            formatted_text += f"Full content limited to {max_tokens_per_source} tokens: {raw}\n\n"
    return formatted_text.strip()

def format_sources(search_results):
    return '\n'.join(f"* {s['title']} : {s['url']}" for s in search_results['results'])

def tavily_search(query, include_raw_content=True, max_results=3):
    return tavily_client.search(query, max_results=max_results, include_raw_content=include_raw_content)

query_writer_prompt = """Your goal is to generate targeted web search query.

The query will gather information related to a specific topic.

Topic:
{research_topic}

Return your query as a JSON object:
{{
    "query": "string",
    "aspect": "string",
    "rationale": "string"
}}"""

summarizer_prompt = """Your goal is to generate a high-quality summary of the web search results.
Instructions:
- Highlight relevant information from each source
- Avoid redundancy and repetition
- Maintain technical depth and coherence
- No preambles or "Based on the above" statements
"""

reflection_prompt = """You are analyzing a summary about "{research_topic}".
1. Identify knowledge gaps.
2. Generate a follow-up question.

Return JSON:
{{
  "knowledge_gap": "string",
  "follow_up_query": "string"
}}"""

@dataclass
class SummaryState:
    research_topic: str
    search_query: str = None
    web_research_results: Annotated[list, operator.add] = field(default_factory=list)
    sources_gathered: Annotated[list, operator.add] = field(default_factory=list)
    research_loop_count: int = 0
    running_summary: str = None

def generate_query(state: SummaryState):
    prompt = query_writer_prompt.format(research_topic=state.research_topic)
    result = llm_json_mode.invoke([SystemMessage(content=prompt), HumanMessage(content="Generate query")])
    parsed = json.loads(result.content)
    state.search_query = parsed['query']

def perform_web_research(state: SummaryState):
    results = tavily_search(state.search_query, max_results=1)
    formatted_sources = deduplicate_and_format_sources(results, os.getenv("MAX_TOKENS_PER_SOURCE"))
    state.web_research_results.append(formatted_sources)
    state.sources_gathered.append(format_sources(results))
    state.research_loop_count += 1

def summarize(state: SummaryState):
    human_input = (
        f"Extend the existing summary: {state.running_summary}\n\nInclude new search results: {state.web_research_results[-1]}\n\nTopic: {state.research_topic}"
        if state.running_summary else
        f"Generate a summary of these search results: {state.web_research_results[-1]}\n\nTopic: {state.research_topic}"
    )
    result = llm.invoke([SystemMessage(content=summarizer_prompt), HumanMessage(content=human_input)])
    state.running_summary = result.content

def reflect(state: SummaryState):
    result = llm_json_mode.invoke([
        SystemMessage(content=reflection_prompt.format(research_topic=state.research_topic)),
        HumanMessage(content=state.running_summary)
    ])
    try:
        follow_up = json.loads(result.content)
        state.search_query = follow_up['follow_up_query']
    except Exception:
        state.search_query = f"{state.research_topic} latest news"

def finalize(state: SummaryState):
    return {
        "topic": state.research_topic,
        "summary": state.running_summary,
        "sources": "\n".join(state.sources_gathered)
    }

def run_research_pipeline(topic: str):
    state = SummaryState(research_topic=topic)
    generate_query(state)
    while state.research_loop_count < os.getenv("MAX_WEB_RESEARCH_LOOPS"):
        perform_web_research(state)
        summarize(state)
        reflect(state)

    final_output = finalize(state)
    try:
        requests.post(os.getenv("BACKEND_API_URL"), json=final_output)
    except Exception:
        pass  # Fail silently

# Auto-run when server starts
if __name__ == "__main__":
    run_research_pipeline("Christiano Ronaldo")  # Or call with any topic
