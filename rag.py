from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

DB_PATH = "index"

embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
db = FAISS.load_local(DB_PATH, embeddings, allow_dangerous_deserialization=True)

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

def answer_question(query):
    docs = db.similarity_search(query, k=4)

    context = ""
    pages = set()

    for d in docs:
        context += d.page_content + "\n"
        pages.add(d.metadata["page"])

    prompt = f"""
You are an assistant answering ONLY from the context.

Context:
{context}

Question: {query}

If the answer is not in the context, say you don't know.
"""

    res = llm.invoke([
        SystemMessage(content="You are a helpful enterprise assistant."),
        HumanMessage(content=prompt)
    ])

    return res.content, sorted(list(pages))


if __name__ == "__main__":
    print(answer_question("What is the revenue growth?"))
