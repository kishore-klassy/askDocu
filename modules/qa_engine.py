import os
import requests
from dotenv import load_dotenv

class QAEngine:
    def __init__(self, vector_store):
        load_dotenv()  # Load environment variables from .env file
        self.vector_store = vector_store
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
        self.headers = {
            "Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"
        }

    def answer_question(self, question):
        relevant_docs = self.vector_store.query(question, top_k=3)

        if not relevant_docs:
            return ("Sorry, I couldn't find any information in the documentation.", [])

        context = "\n\n".join([doc['text'] for doc in relevant_docs])

        prompt = (
            f"Answer the question based on the following documentation context. "
            f"If the answer is not contained in the context, say you don't know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {question}\nAnswer:"
        )

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 256,
                        "temperature": 0.2
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            generated = result[0]["generated_text"]
            answer = generated.split('Answer:')[-1].strip()

            if "i don't know" in answer.lower() or answer == "":
                answer = "Sorry, I couldn't find any information about that in the documentation."

            sources = [doc['url'] for doc in relevant_docs]
            return answer, sources

        except Exception as e:
            return f"Error during question answering: {str(e)}", []
