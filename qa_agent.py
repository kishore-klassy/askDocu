# File: qa_agent.py
import argparse
from modules.crawler import crawl_help_site
from modules.vector_store import create_or_load_vector_store
from modules.qa_engine import QAEngine

def main():
    parser = argparse.ArgumentParser(description="AI-powered Help Website QA Agent")
    parser.add_argument("--url", required=True, help="Help website base URL to crawl")
    args = parser.parse_args()

    try:
        print(f"Crawling documentation from {args.url} ...")
        docs = crawl_help_site(args.url)
        if not docs:
            print("No documentation content found. Please check the URL and try again.")
            return

        print(f"Processing and indexing {len(docs)} pages ...")
        vector_store = create_or_load_vector_store(docs)

        qa_engine = QAEngine(vector_store)
    except ValueError as e:
        print(f"Configuration error: {e}")
        return
    except Exception as e:
        print(f"Failed to initialize QA agent: {e}")
        return

    print("Agent ready. Ask your questions (type 'exit' to quit):")
    while True:
        try:
            query = input("> ").strip()
            if query.lower() in ('exit', 'quit'):
                print("Goodbye!")
                break

            if not query:
                print("Please enter a question.")
                continue

            answer, sources = qa_engine.answer_question(query)
            print(f"\nAnswer:\n{answer}\n")
            if sources:
                print("Sources:")
                for src in sources:
                    print(f"- {src}")
            print("-" * 60)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error processing question: {e}")
            continue

if __name__ == "__main__":
    main()
 