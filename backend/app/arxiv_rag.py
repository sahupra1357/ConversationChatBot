# RAG system: Dynamic arXiv query, lazy vectorization, and retrieval (Class-based)

import requests
import uuid
import xml.etree.ElementTree as ET
from threading import Thread
from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from llama_index.core.schema import TextNode
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.settings import Settings
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import SentenceSplitter
from PyPDF2 import PdfReader
from typing import Optional
from llama_index.llms.openai import OpenAI
import io

import os
from dotenv import load_dotenv
# Load environment variables
load_dotenv()
from app.observability import init_observability
# Initialize observability
init_observability()


QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "arxiv_ml_papers")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
MAX_RESULTS = int(os.getenv("MAX_RESULTS", 2))
SHORT_SUMMARY_LENGTH = int(os.getenv("SHORT_SUMMARY_LENGTH", 100))
VECTOR_DIM = int(os.getenv("VECTOR_DIM", 1536))

class ArxivRAG:
    def __init__(self,
                 qdrant_host=QDRANT_HOST,
                 qdrant_port=QDRANT_PORT,
                 collection_name=COLLECTION_NAME,
                 embed_model_name=EMBED_MODEL,
                 max_results=MAX_RESULTS,
                 vector_dim=VECTOR_DIM):
        """ Initialize the ArxivRAG system.
        Args:
            qdrant_host (str): Qdrant host address.
            qdrant_port (int): Qdrant port number.
            collection_name (str): Name of the Qdrant collection.
            embed_model_name (str): Name of the embedding model to use.
            max_results (int): Maximum number of results to fetch from arXiv.
            vector_dim (int): Dimension of the embedding vectors.
        """

        self.collection_name = collection_name
        self.max_results = max_results

        self.embed_model = OpenAIEmbedding(model=embed_model_name)
        Settings.embed_model = self.embed_model
        Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
        Settings.num_output = 512
        Settings.context_window = 3900

        self.qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_dim, distance=Distance.COSINE)
        )

        self.vector_store = QdrantVectorStore(client=self.qdrant_client, collection_name=collection_name)

    def fetch_arxiv_feed(self, query):
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&sortBy=submittedDate&sortOrder=descending&max_results={self.max_results}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to fetch from arXiv")
        return response.text

    def extract_arxiv_pdf_text(self, arxiv_id):
        """
        Download an arXiv PDF by ID and extract its text, all in memory.
        """
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        response = requests.get(pdf_url)
        response.raise_for_status()
        pdf_filelike = io.BytesIO(response.content)
        reader = PdfReader(pdf_filelike)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text

    def parse_arxiv_feed(self, feed_xml):
        root = ET.fromstring(feed_xml)
        entries = []
        for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
            title = entry.find("{http://www.w3.org/2005/Atom}title").text.strip()
            summary = entry.find("{http://www.w3.org/2005/Atom}summary").text.strip()
            link = entry.find("{http://www.w3.org/2005/Atom}id").text.strip()
            arxiv_id = link.split('/')[-1]
            full_text = self.extract_arxiv_pdf_text(arxiv_id)
            entries.append({"title": title, "summary": summary, "link": link, "full_text": full_text, "arxiv_id": arxiv_id})

        if entries:
            print(f"Found {len(entries)} new papers in arXiv feed.")
            print(f"Example paper: {entries[0]['title']} -- {entries[0]['summary']} -- ({entries[0]['link']})")

        return entries

    def is_already_indexed(self, link):
        result, _ = self.qdrant_client.scroll(
            collection_name=self.collection_name,
            scroll_filter={"must": [{"key": "source", "match": {"value": link}}]},
            limit=1
        )
        return len(result) > 0

    def chunk_text(self,text, chunk_size=2000):
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def create_nodes_from_papers(self, entries, chunk_size=2000):
        nodes = []
        paper_summaries = []
        for paper in entries:
            if self.is_already_indexed(paper['link']):
                print(f"Skipping already indexed paper: {paper['title']}")
                continue
            # Create a summary for the paper
            summary_snippet = paper['summary'][:SHORT_SUMMARY_LENGTH]
            last_index = summary_snippet.rindex(".") if "." in summary_snippet else len(summary_snippet)
            short_summary = summary_snippet[:last_index] + "..." if len(summary_snippet) > SHORT_SUMMARY_LENGTH else summary_snippet            
            paaper_summary = f"📄 Title: {paper['title']}\n 🔗 link: {paper['link']}\n 📝papaer_summary: {short_summary}\n\n"
            paper_summaries.append(paaper_summary)


            text = f"Title: {paper['title']}\npapaer_summary: {paper['summary']}\nlink: {paper['link']}\n\nFull Text:\n{paper['full_text']}"
            chunks = self.chunk_text(text, chunk_size)
            for idx, chunk in enumerate(chunks):
                node = TextNode(
                    text=chunk,
                    metadata={
                        "title": paper['title'],
                        "papaer_summary": paper['summary'],
                        "link": paper['link'],
                        "chunk": idx + 1
                    }
                )
                node.node_id = str(uuid.uuid4())
                nodes.append(node)
        return nodes, paper_summaries

    def vectorize_and_store(self, nodes):
        for node in nodes:
            embedding = self.embed_model.get_text_embedding(node.get_content())
            node.embedding = embedding  # Set the embedding attribute on the node
            self.vector_store.add([node], embeddings=[embedding])

    def vector_store_has_documents(self,user_question: str) -> bool:
        """
        Checks whether the Qdrant collection contains any indexed documents (points).

        Returns:
            bool: True if at least one point exists in the collection, False otherwise.
        """
        try:
            count_result = self.qdrant_client.count(
                collection_name=COLLECTION_NAME,
                exact=True  # Ensure an accurate count
            )
            print(f"Vector store contains {count_result.count} documents.")
            return count_result.count > 0
        except Exception as e:
            print(f"⚠️ Failed to check vector store content: {e}")
            return False

    def query_qdrant(self,user_question: str) -> str:
        """First searches Qdrant for relevant papers based on user's question."""
        if not self.qdrant_client.collection_exists(COLLECTION_NAME):
            return "No papers stored yet. Ask me to fetch some first."

        # Build the index from the vector store with settings
        index = VectorStoreIndex.from_vector_store(self.vector_store, settings=Settings)

        # Retrieve relevant nodes
        retriever = VectorIndexRetriever(index=index, similarity_top_k=MAX_RESULTS)
        retrieved_nodes = retriever.retrieve(user_question)

        return retrieved_nodes

    def summarize_with_llm(self, context: str, question: str, llm: Optional[OpenAI] = None):
        """
        Generate a summary of the context based on the user's question using the same LLM used in the agent.

        Args:
            context (str): Extracted content from vector DB
            question (str): User's question
            llm (OpenAI, optional): Shared LLM instance

        Returns:
            str: Summary generated by the LLM
        """
        if llm is None:
            raise ValueError("LLM instance is required")

        prompt = f"""You are a research assistant. Given the following academic content, answer the question concisely.

            Context:
            {context}

            Question:
            {question}

            Answer:
        """

        response = llm.complete(prompt)
        return response.text.strip()


# --- Lazy Load Function ---
def get_lazy_load_and_query(llm):

    rag = ArxivRAG()
    def lazy_load_and_query(user_question: str):
        """
        Handle a user query by checking the vector store first and falling back to LLM if needed.

        This function checks if the Qdrant vector store contains relevant data for the given user question.
        - If data exists in the vector DB, it uses `query_qdrant(user_question)` to retrieve a relevant response.
        - If no data is found (e.g., the vector store is empty or not relevant), it calls an LLM to generate the response.

        Args:
            user_question (str): The natural language question provided by the user.

        Returns:
            str: A response generated either from vector search or from a fallback LLM.

        Notes:
            This function acts as a smart routing layer to avoid unnecessary LLM calls if embeddings already cover the query context.
        """
        print(f"Fetching relevant papers for query: '{user_question}'")

        retrieved_nodes = []
        llm_summary = "No relevant papers found."
        if not rag.vector_store_has_documents(user_question):
            feed = rag.fetch_arxiv_feed(query=user_question)
            entries = rag.parse_arxiv_feed(feed)
            nodes, paper_summaries = rag.create_nodes_from_papers(entries)
            if nodes:
                # Initialize Qdrant vector store
                print(f"Vector store initialized with collection '{COLLECTION_NAME}'")
                print(f"Number of new papers to index: {len(nodes)}")
                thread = Thread(target=rag.vectorize_and_store, args=(nodes,))
                thread.start()            
                return paper_summaries
            else:
                print("No new papers to index.")

        print("Vector store has documents, querying Qdrant...")
        retrieved_nodes = rag.query_qdrant(user_question)

        paper_summaries = []
        for node in retrieved_nodes:
            metadata = node.metadata or {}
            title = metadata.get("title", "Untitled")
            summary = metadata.get("papaer_summary", "No summary available")
            summary_snippet = summary[:SHORT_SUMMARY_LENGTH]
            last_index = summary_snippet.rindex(".") if "." in summary_snippet else len(summary_snippet)
            short_summary = summary[:last_index] + "..." if len(summary) > SHORT_SUMMARY_LENGTH else summary            
            link = metadata.get("link", "No link")
            paper_summaries.append(f"📄 {title}\n\n🔗 {link}\n\n📝 {short_summary}\n{node.get_content()}")

        return paper_summaries



        # Concatenate retrieved content for LLM summarization
        # context = "\n\n".join(node.get_content() for node in retrieved_nodes)
        # print(f"Retrieved {len(retrieved_nodes)} relevant nodes from vector store.")
        # print(f"Context length: {len(context)} characters")
        # return context
        # max_context_chars = 6000
        # if len(context) > max_context_chars:
        #     context = context[:max_context_chars]

        # llm_summary = rag.summarize_with_llm(context, user_question, llm=llm)

        # return llm_summary
    
    return lazy_load_and_query

# --- Run Example ---
if __name__ == "__main__":
    rag = ArxivRAG()
    user_query = "Summarize recent advancements in machine learning"
    papers = rag.query(user_query)
    print("\nLatest Papers:")
    for paper in papers:
        print(f"- {paper['title']}\n  {paper['link']}\n")