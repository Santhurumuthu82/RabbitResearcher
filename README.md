
# 🧠 Local Research Summarizer

A fully local, privacy-friendly web research assistant that uses a local LLM (via [Ollama](https://ollama.com)) and the [Tavily Search API](https://docs.tavily.com/) to iteratively gather, reflect on, and summarize information from the web.

## 🚀 Features

- 🔍 **Automated Web Search** with Tavily
- 🧠 **Local LLM Summarization** via Ollama (`gemma3:1b`, `llama3`, etc.)
- ♻️ **Iterative Reflection**: Fills knowledge gaps with follow-up queries
- 📄 **Structured Summary Output** with links to sources
- 🛡️ **Privacy-first**: No cloud LLM usage

## 📦 Dependencies

Install Python dependencies:

```bash
pip install -r requirements.txt
```

`requirements.txt` should include:

```text
langchain
langchain-core
langchain-ollama
tavily
```

Also make sure you have:

- ✅ [Ollama installed and running](https://ollama.com)
- ✅ [Tavily API key](https://app.tavily.com) — set it via environment variable or config

## 🧰 Configuration

Set your Tavily API key:

```bash
export TAVILY_API_KEY=your_api_key_here
```

## 🧪 Example Usage

```bash
python research_agent.py
```

This will search and summarize a hardcoded topic like:

```python
topic = "Recent advancements in quantum computing"
```

You can change this in the `run_research_pipeline()` call or expose it via CLI.

## 🛠 How It Works

1. **Query Generator**: Creates a targeted query from a user-supplied topic.
2. **Web Research**: Uses Tavily to get relevant content and raw text.
3. **Summarization**: A local LLM creates or extends a technical summary.
4. **Reflection**: Identifies gaps and generates a follow-up query.
5. **Loop**: Repeats up to N times for deeper exploration.
6. **Final Output**: Outputs the summary and sources in markdown format.

## 📁 File Structure

```
.
├── research_agent.py     # Main pipeline
├── README.md             # This file
├── requirements.txt      # Python dependencies
```

## 🧠 Example Output

```markdown
## Summary

Quantum computing has recently...

### Sources:
* Title 1 : https://example.com
* Title 2 : https://example.com
```

## 📝 License

MIT License
