# RAG system: Dynamic arXiv query, lazy vectorization, and retrieval (Class-based)

import requests
import uuid
import xml.etree.ElementTree as ET
from threading import Thread
from datetime import datetime
import os
import time
import random
import json
import urllib.parse
from typing import Dict, List, Optional, Tuple

from llama_index.core import VectorStoreIndex, ServiceContext
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.settings import Settings
from llama_index.core.schema import TextNode
from llama_index.core.node_parser import SentenceSplitter
from PyPDF2 import PdfReader
from typing import Optional, List, Dict, Any
from llama_index.core.llms import LLM
from app.llm_providers import get_llm
import io
import time
import random

import os
#from dotenv import load_dotenv
# Load environment variables
#load_dotenv()
from app.observability import init_observability
from app.config import local_settings
# Initialize observability
init_observability()

QDRANT_HOST = local_settings.QDRANT_HOST
QDRANT_PORT = local_settings.QDRANT_PORT
COLLECTION_NAME = local_settings.COLLECTION_NAME
OPENAI_EMBED_MODEL = local_settings.OPENAI_EMBED_MODEL
OLLAMA_EMBED_MODEL = local_settings.OLLAMA_EMBED_MODEL
MAX_RESULTS = local_settings.MAX_RESULTS
SHORT_SUMMARY_LENGTH = local_settings.SHORT_SUMMARY_LENGTH
VECTOR_DIM = local_settings.VECTOR_DIM

# Retry configuration for external API calls
MAX_RETRIES = local_settings.MAX_RETRIES
RETRY_DELAY_BASE = local_settings.RETRY_DELAY_BASE
RETRY_JITTER = local_settings.RETRY_JITTER

class ArxivRAG:
    def __init__(self,
                 qdrant_host=QDRANT_HOST,
                 qdrant_port=QDRANT_PORT,
                 collection_name=COLLECTION_NAME,
                 embed_model_name=OLLAMA_EMBED_MODEL if local_settings.LLM_PROVIDER.lower() == "ollama" else OPENAI_EMBED_MODEL,
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

        # Choose the embedding model based on the name
        if "bge" in embed_model_name:
            print(f"Using HuggingFace embedding model: {embed_model_name}")
            self.embed_model = HuggingFaceEmbedding(model_name=embed_model_name)
        else:
            print(f"Using OpenAI embedding model: {embed_model_name}")
            self.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
            
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
        """
        Fetch arXiv papers based on a query with improved error handling and retry logic.
        """
        url = f"http://export.arxiv.org/api/query?search_query=all:{query}&sortBy=submittedDate&sortOrder=descending&max_results={self.max_results}"
        print(f"Querying arXiv API with URL: {url}")
        
        retry_count = 0
        last_exception = None
        
        while retry_count < MAX_RETRIES:
            try:
                # Add user-agent to mimic a browser (sometimes helps with rate limiting)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
                }
                
                # Make the request with exponential backoff if retrying
                if retry_count > 0:
                    # Calculate delay with exponential backoff and jitter
                    delay = RETRY_DELAY_BASE * (2 ** (retry_count - 1)) + random.uniform(0, RETRY_JITTER)
                    print(f"Retry {retry_count}/{MAX_RETRIES} after {delay:.2f} seconds...")
                    time.sleep(delay)
                
                # Make the request
                response = requests.get(url, headers=headers, timeout=30)
                
                # Handle 503 specifically with a more detailed message
                if response.status_code == 503:
                    print(f"arXiv API returned 503 Service Unavailable. This usually indicates rate limiting or temporary maintenance.")
                    retry_count += 1
                    last_exception = Exception(f"arXiv API is temporarily unavailable (HTTP 503). Retry {retry_count}/{MAX_RETRIES}")
                    continue
                
                # For other status codes, proceed as normal
                response.raise_for_status()
                
                print(f"arXiv API response status: {response.status_code}")
                
                # Verify we got valid XML data
                content_type = response.headers.get('Content-Type', '')
                content_length = len(response.text)
                
                if 'xml' not in content_type.lower() and content_length < 100:
                    print(f"Warning: Response may not be valid XML. Content-Type: {content_type}")
                    print(f"Response preview: {response.text[:100]}...")
                
                # Success! Return the response
                return response.text
                
            except requests.exceptions.HTTPError as e:
                # Log the error
                error_msg = f"arXiv API HTTP error: {e}"
                print(f"Error: {error_msg}")
                
                # Handle specific status codes
                if e.response.status_code in [429, 503]:  # Too many requests or Service Unavailable
                    retry_count += 1
                    last_exception = e
                    print(f"Rate limiting detected. Will retry ({retry_count}/{MAX_RETRIES})...")
                else:
                    # For other HTTP errors, don't retry
                    raise Exception(error_msg)
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # Network-related errors are worth retrying
                error_type = "timeout" if isinstance(e, requests.exceptions.Timeout) else "connection error"
                error_msg = f"arXiv API {error_type}: {e}"
                print(f"Error: {error_msg}")
                
                retry_count += 1
                last_exception = e
                print(f"Will retry ({retry_count}/{MAX_RETRIES})...")
                
            except Exception as e:
                # For unexpected errors, don't retry
                error_msg = f"Unexpected error fetching from arXiv: {str(e)}"
                print(f"Error: {error_msg}")
                raise Exception(error_msg)
        
        # If we exhausted all retries
        if last_exception:
            error_msg = f"Failed to fetch from arXiv after {MAX_RETRIES} attempts: {str(last_exception)}"
            print(f"Error: {error_msg}")
            raise Exception(error_msg)

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
        """
        Parse arXiv XML feed with improved error handling.
        """
        try:
            # Try to parse XML
            root = ET.fromstring(feed_xml)
            
            # Define namespaces for extracting data
            namespaces = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            # Initialize an empty list to store paper information
            papers = []
            
            # Find entries using namespace
            entries = root.findall('.//atom:entry', namespaces)
            if not entries:
                print("Warning: No entries found in arXiv response")
                print(f"Response preview: {feed_xml[:200]}...")
                return []
                
            print(f"Found {len(entries)} papers in arXiv response")
            
            # Process each entry (paper)
            for entry in entries:
                try:
                    # Extract PDF link
                    link = entry.find('./atom:link[@title="pdf"]', namespaces)
                    pdf_link = link.get('href') if link is not None else None
                    # If PDF link is not present, skip this entry
                    if pdf_link is None:
                        print("Warning: No PDF link found for entry")
                        continue
                    else:
                        # If PDF link is present, proceed with extracting information
                        if not self.is_already_indexed(pdf_link.split('/')[-1]):
                            print(f"Not indexed paper: {pdf_link}")
                            pass
                        else:
                            print(f"Skipping already indexed paper: {pdf_link}")
                            continue

                    # Extract basic information
                    title = entry.find('./atom:title', namespaces)
                    summary = entry.find('./atom:summary', namespaces)
                    published = entry.find('./atom:published', namespaces)
                    authors_elements = entry.findall('./atom:author/atom:name', namespaces)
                    
                    # Skip if essential elements are missing
                    if title is None or summary is None:
                        continue
                        
                    # Format title and summary (clean up newlines and spaces)
                    title_text = title.text.replace('\n', ' ').strip() if title.text else "No title"
                    summary_text = summary.text.replace('\n', ' ').strip() if summary.text else "No summary"
                    
                    # Format publication date
                    pub_date = published.text if published is not None and published.text else "No date"
                    if pub_date != "No date":
                        # Try to parse and format date
                        try:
                            date_obj = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                            pub_date = date_obj.strftime("%Y-%m-%d")
                        except (ValueError, TypeError) as e:
                            print(f"Warning: Could not parse date '{pub_date}': {e}")
                    
                    # Extract authors
                    authors = [author.text for author in authors_elements if author.text]
                    author_text = ", ".join(authors) if authors else "Unknown"
                    

                    # Download and extract text from the PDF
                    try:
                        full_text = self.extract_arxiv_pdf_text(entry.get('id', '').split('/')[-1])
                        # full_text = "Extracted text from PDF for demonstration purposes will implement later"
                    except Exception as e:
                        print(f"Error extracting PDF text: {e}")
                        full_text = "No text extracted"

                    # Create a formatted entry for the paper
                    paper_info = {
                        'title': title_text,
                        'summary': summary_text,
                        'authors': author_text,
                        'published_date': pub_date,
                        'pdf_link': pdf_link,
                        'full_text': full_text
                    }

                    #print(f"Processed paper: -->  {paper_info}")

                    papers.append(paper_info)
                except Exception as e:
                    # If processing a specific paper fails, log the error but continue with others
                    print(f"Error processing a paper entry: {e}")
                    continue
            
            # Return the list of papers
            return papers
            
        except ET.ParseError as e:
            error_msg = f"XML parsing error: {str(e)}"
            line_number = getattr(e, 'position', (0, 0))[0]
            print(f"Error: {error_msg} at line {line_number}")
            
            # Try to show the problematic XML around the error
            if line_number > 0:
                lines = feed_xml.split('\n')
                if line_number <= len(lines):
                    context_start = max(0, line_number - 2)
                    context_end = min(len(lines), line_number + 2)
                    print("XML context around error:")
                    for i in range(context_start, context_end):
                        print(f"{i+1}: {lines[i]}")
            
            raise Exception(error_msg)
            
        except Exception as e:
            error_msg = f"Error parsing arXiv response: {str(e)}"
            print(f"Error: {error_msg}")
            print(f"Response preview: {feed_xml[:200]}...")
            raise Exception(error_msg)

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
            #print(f"Processing paper: {paper['title']} inside create_nodes_from_papers")
            # Create a summary for the paper
            summary_snippet = paper['summary'][:SHORT_SUMMARY_LENGTH]
            last_index = summary_snippet.rindex(".") if "." in summary_snippet else len(summary_snippet)
            short_summary = summary_snippet[:last_index] + "..." if len(summary_snippet) > SHORT_SUMMARY_LENGTH else summary_snippet
            paper_summary = f"📄 Title: {paper['title']}\n 🔗 link: {paper['pdf_link']}\n authors: {paper['authors']}\n published_date: {paper['published_date']}\n 📝paper_summary: {short_summary}\n\n"
            paper_summaries.append(paper_summary)

            #print(f"Creating nodes for paper: {paper['title']} before chunking")

            text = f"Title: {paper['title']}\npaper_summary: {paper['summary']}\nlink: {paper['pdf_link']}\nauthors: {paper['authors']}\npublished_date: {paper['published_date']}\n\n\nFull Text:\n{paper['full_text']}"
            chunks = self.chunk_text(text, chunk_size)
            for idx, chunk in enumerate(chunks):
                node = TextNode(
                    text=chunk,
                    metadata={
                        "title": paper['title'],
                        "paper_summary": paper['summary'],
                        "link": paper['pdf_link'],
                        "authors": paper['authors'],
                        "chunk": idx + 1
                    }
                )
                node.node_id = str(uuid.uuid4())
                nodes.append(node)
            
            #print(f"Created {len(chunks)} nodes for paper: {paper['title']}")
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

    def summarize_with_llm(self, context: str, question: str, llm: Optional[LLM] = None):
        """
        Generate a summary of the context based on the user's question using the same LLM used in the agent.

        Args:
            context (str): Extracted content from vector DB
            question (str): User's question
            llm (LLM, optional): Shared LLM instance

        Returns:
            str: Summary generated by the LLM
        """
        if llm is None:
            # Use default LLM from settings if none provided
            llm = get_llm(
                provider=local_settings.LLM_PROVIDER,
                model_name=local_settings.OLLAMA_MODEL if local_settings.LLM_PROVIDER.lower() == "ollama" else local_settings.OPENAI_MODEL
            )

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
def get_lazy_load_and_query(llm: Optional[LLM] = None):
    """
    Get a function that can lazy load papers and query them.
    
    Args:
        llm (LLM, optional): LLM instance to use for summarization
        
    Returns:
        function: A function that can be used as a tool for the agent
    """
    if llm is None:
        # Use default LLM from settings
        llm = get_llm(
            provider=local_settings.LLM_PROVIDER,
            model_name=local_settings.OLLAMA_MODEL if local_settings.LLM_PROVIDER.lower() == "ollama" else local_settings.OPENAI_MODEL
        )

    # Use the proper embedding model based on configuration
    embed_model=OLLAMA_EMBED_MODEL if local_settings.LLM_PROVIDER.lower() == "ollama" else OPENAI_EMBED_MODEL,

    rag = ArxivRAG(embed_model_name=embed_model)
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
        try:
            if not rag.vector_store_has_documents(user_question):
                try:
                    feed = rag.fetch_arxiv_feed(query=user_question)
                    entries = rag.parse_arxiv_feed(feed)
                    
                    if not entries:
                        return ["I couldn't find any relevant papers on arXiv for your query. Could you try rephrasing or using more specific keywords?"]

                    # print(f"Found {len(entries)} new papers to index.")
                    # Create nodes from the fetched papers    
                    nodes, paper_summaries = rag.create_nodes_from_papers(entries)
                    if nodes:
                        # Initialize Qdrant vector store
                        #print(f"Vector store initialized with collection '{COLLECTION_NAME}'")
                        #print(f"Number of new papers to index: {len(nodes)}")
                        thread = Thread(target=rag.vectorize_and_store, args=(nodes,))
                        thread.start()            
                        return paper_summaries
                    else:
                        #print("No new papers to index.")
                        return ["I found some papers, but they were already in my database. Let me search for relevant information..."]
                except Exception as e:
                    error_msg = str(e)
                    print(f"Error fetching from arXiv: {error_msg}")
                    
                    # Provide specific error messages based on the error type
                    if "503" in error_msg or "Service Unavailable" in error_msg:
                        return ["I'm currently experiencing difficulty connecting to the arXiv research database due to high traffic or temporary maintenance. Please try again in a few minutes. In the meantime, I can answer based on my existing knowledge."]
                    elif "429" in error_msg or "Too Many Requests" in error_msg:
                        return ["I've reached the rate limit for arXiv's API. This typically happens when there are many research requests in a short period. Please try again in a few minutes."]
                    elif "timeout" in error_msg.lower():
                        return ["The connection to arXiv's research database timed out. This might be due to network issues or high server load. Please try again shortly."]
                    else:
                        return [f"I encountered an issue connecting to arXiv: {error_msg}. Let me try to answer based on my existing knowledge instead."]

            #print("Vector store has documents, querying Qdrant...")
            retrieved_nodes = rag.query_qdrant(user_question)

            if not retrieved_nodes:
                return ["I couldn't find any specific papers that match your query in my database. Could you try a different question?"]

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
            
        except Exception as e:
            error_msg = str(e)
            print(f"Unexpected error in lazy_load_and_query: {error_msg}")
            
            # Provide more specific error messages based on keywords in the error
            if "Failed to fetch from arXiv" in error_msg:
                return ["I'm having trouble connecting to the arXiv research database at the moment. This could be due to network issues or rate limiting. I can still help answer your question based on my general knowledge. What would you like to know?"]
            elif "vector store" in error_msg.lower() or "qdrant" in error_msg.lower():
                return ["I'm experiencing an issue with my research database. This is likely a temporary problem. Let me try to answer based on my general knowledge instead."]
            elif "timeout" in error_msg.lower():
                return ["The operation timed out while processing your request. This might be due to the complexity of your query or temporary server load. Could you try a simpler question?"]
            else:
                return [f"I encountered an unexpected error while researching your question. Please try again with a different query. Technical details: {error_msg}"]
    
    return lazy_load_and_query

# --- Run Example ---
if __name__ == "__main__":
    rag = ArxivRAG()
    user_query = "Summarize recent advancements in machine learning"
    papers = rag.query(user_query)
    print("\nLatest Papers:")
    for paper in papers:
        print(f"- {paper['title']}\n  {paper['link']}\n")