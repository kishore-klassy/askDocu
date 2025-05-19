# File: qa_agent.py
import argparse
from modules.crawler import crawl_help_site
from modules.vector_store import create_or_load_vector_store
from modules.qa_engine import QAEngine

def main():
    parser = argparse.ArgumentParser(description="AI-powered Help Website QA Agent")
    parser.add_argument("--url", required=True, help="Help website base URL to crawl")
    args = parser.parse_args()

    print(f"Crawling documentation from {args.url} ...")
    docs = crawl_help_site(args.url)
    if not docs:
        print("No documentation content found. Exiting.")
        return

    print(f"Processing and indexing {len(docs)} pages ...")
    vector_store = create_or_load_vector_store(docs)

    
    qa_engine = QAEngine(vector_store)

    print("Agent ready. Ask your questions (type 'exit' to quit):")
    while True:
        query = input("> ").strip()
        if query.lower() in ('exit', 'quit'):
            print("Goodbye!")
            break

        answer, sources = qa_engine.answer_question(query)
        print(f"\nAnswer:\n{answer}\n")
        if sources:
            print("Sources:")
            for src in sources:
                print(f"- {src}")
        print("-" * 60)

if __name__ == "__main__":
    main()
 