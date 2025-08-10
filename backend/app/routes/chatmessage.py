from fastapi import Form
from llama_index.llms.openai import OpenAI
from llama_index.core.settings import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.prompts import PromptTemplate
import os
from app.config import local_settings
from llama_index.core.agent.workflow import ReActAgent
from app.arxiv_rag import get_lazy_load_and_query
from fastapi import APIRouter


# Initialize OpenAI LLM and LlamaIndex ReActAgent
llm = OpenAI(model=local_settings.OPENAI_MODEL, temperature=0.0, max_tokens=512)
Settings.llm = llm
Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=20)
Settings.num_output = 512
Settings.context_window = 3900

def read_prompt_file(file_path):
    """Read the system prompt from a file."""
    with open(file_path, 'r') as file:
        return file.read().strip()


lazy_load_and_query = get_lazy_load_and_query(llm=llm)
agent = ReActAgent(llm=llm, 
                   tools=[lazy_load_and_query],
                   verbose=True,)

system_prompt = read_prompt_file("app/system_prompt.txt")
agent.update_prompts({"react_header": PromptTemplate(system_prompt)})

router = APIRouter(tags=["chat"])

@router.post("/chat")
async def chat_endpoint(
    message: str = Form(...),
    memory: str = Form(""),
):
    # For now, just append memory to the message if provided
    user_message = message
    if memory:
        user_message = f"[Memory: {memory}]\n{message}"
    # response = agent.chat(user_message)
    response = await agent.run(user_message)
    print(f"User message: {user_message}")
    return {"response": response}
