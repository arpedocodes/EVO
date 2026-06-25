from ollama import chat
from tavily import TavilyClient
from dotenv import load_dotenv
import os
import concurrent.futures

load_dotenv()

client = TavilyClient(os.getenv("TAVILY_TOKEN_1"))


def search(query: str):
    response = client.search(
        query=query,
        search_depth="advanced"
    )

    return {
        "type": "search",
        "input": query,
        "response": response
    }


def extract(urls: list[str]):
    response = client.extract(
        urls=urls,
        extract_depth="advanced"
    )

    return {
        "type": "extract",
        "input": urls,
        "response": response
    }


def crawl(url: str):
    response = client.crawl(url)

    return {
        "type": "crawl",
        "input": url,
        "response": response
    }


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def research(questions: list[str], max_parallel: int = 5):
    all_search_results = []

    for batch in chunk_list(questions, max_parallel):

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(batch)
        ) as executor:

            futures = {
                executor.submit(search, question): question
                for question in batch
            }

            for future in concurrent.futures.as_completed(futures):

                question = futures[future]

                try:
                    result = future.result()

                    all_search_results.append({
                        "question": question,
                        "response": result
                    })

                except Exception as e:
                    print(f"Search failed: {question}")
                    print(e)
    return all_search_results

def build_context(search_result: dict, max_content_chars: int = 1000) -> str:
    response = search_result.get("response", {})
    query = response.get("query", "")
    results = response.get("results", [])

    parts = [
        f"# Search Query\n{query}\n",
        f"# Found {len(results)} Results\n"
    ]

    for i, result in enumerate(results, start=1):
        content = result.get("content", "").strip()

        if len(content) > max_content_chars:
            content = content[:max_content_chars] + "..."

        parts.append(
            f"""
## Result {i}
Title: {result.get('title', 'N/A')}
URL: {result.get('url', 'N/A')}
Score: {result.get('score', 0):.4f}

Content:
{content}
"""
        )

    return "\n".join(parts)

def summarize_context(search_result: dict, context: str) -> str:

    question = search_result["input"]

    results = search_result.get("response", {}).get("results", [])

    urls = []

    for result in results:
        urls.append(result.get("url", "N/A"))

    sources = "\n".join(urls)

    prompt = f"""
Question:
{question}

Research Context:
{context}

Instructions:
- Read the research context carefully.
- Extract only information relevant to the question.
- Remove duplicate information.
- Ignore advertisements and fluff.
- Return only concise bullet points.
- Focus on facts.
- Do not write an introduction.
- Do not write a conclusion.
"""

    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    summary = response["message"]["content"]

    return f"""
QUESTION:
{question}

SUMMARY:
{summary}

SOURCES:
{sources}
"""

def internet_scraper(query,search_type):
    if search_type == "search":
        search_result = search(query)
        context = build_context(search_result)
        summary = summarize_context(search_result,context)
        return summary
    elif search_type == "extract":
        search_result = extract(query)
        context = build_context(search_result)
        summary = summarize_context(search_result,context)
        return summary
    elif search_type == "crawl":
        search_result = crawl(query)
        context = build_context(search_result)
        summary = summarize_context(search_result,context)
        return summary
    else:
        raise ValueError("Invalid search type provided.")

if __name__ == "__main__":
    result = internet_scraper("What is the blue origin explosion news?",search_type="search")
    print(result)