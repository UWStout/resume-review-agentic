# Standard libraries
from os import getenv

# Vectorstore database and ollama embedding interface
from langchain_community.vectorstores import Chroma
from chromadb.config import Settings
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

# For loading and parsing PDFs
from langchain_unstructured import UnstructuredLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Creating a tool from a retriever
from langchain_core.tools.retriever import create_retriever_tool

# Read .env file into environment
from dotenv import load_dotenv
load_dotenv()

# Create constant variables for secrets and config
UNSTRUCTURED_API_KEY = getenv("UNSTRUCTURED_API_KEY", "badkey")
UNSTRUCTURED_HOST = getenv("UNSTRUCTURED_CUSTOM_HOST", "localhost")
UNSTRUCTURED_PORT = getenv("UNSTRUCTURED_CUSTOM_PORT", "5000")

OLLAMA_HOST = getenv("OLLAMA_CUSTOM_HOST", "localhost")
OLLAMA_PORT = getenv("OLLAMA_CUSTOM_PORT", "11434")

EMBEDDING_MODEL_NAME = getenv("EMBEDDING_MODEL_NAME", "qwen3-embedding:8b")

# Setup chroma to disable usage telemetry (keeping things 100% local)
chroma_settings = Settings(anonymized_telemetry=False)

# Embedding model used for creating the vector embeddings
ollamaEmbed = OllamaEmbeddings(
    model=EMBEDDING_MODEL_NAME,
    base_url=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}"
)

def create_resume_rules_tool():
    # Rules for a complete resume as a LangChain Document
    resume_rules_doc = Document(
        page_content="""
            A complete resume should include the following parts:
            1. The applicant's name, email, and a summary/goal/objective section.
            2. Two sections describing educational experience and professional experience.
            3. A section describing one to three projects.
            4. A list of technical skills.
            5. A list of teamwork or soft skills.

            A resume might not label the name of its subject explicitly. If you aren't sure of
            the subject's name, just use the first line of text in the document as their name.
            Contact information (such as a phone number, address, or email) also might not be
            labeled but you should be able to identify it by the structure of the information.
            """,
        metadata={}
    )

    # Constructor vector embedding and return as tool
    complete_vectorstore = Chroma.from_documents(
        client_settings=chroma_settings,
        documents=[resume_rules_doc],
        embedding=ollamaEmbed
    )
    retriever_tool = create_retriever_tool(
        complete_vectorstore.as_retriever(),
        "ResumeRules",
        "Desirable traits for a complete resume"
    )
    return retriever_tool, resume_rules_doc


def create_resume_tool_from_pdf(input_pdf):
    # 1. Load and Vectorize Documents
    # 1.1 Load and parse PDF document
    loader = UnstructuredLoader(
        file_path = input_pdf,
        api_key=UNSTRUCTURED_API_KEY,
        partition_via_api=True,
        chunking_strategy="by_title",
        strategy="auto",
        url=f"http://{UNSTRUCTURED_HOST}:{UNSTRUCTURED_PORT}"
    )
    docs = loader.load()

    # 1.2 Split the text into usable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " "]
    )
    splits = text_splitter.split_documents(docs)
    if not splits:
        print("ERROR: Text splitter returned empty array")
        return None

    # 1.3 Process the resulting split text into a vector store using an embedding LLM
    resume_vectorstore = Chroma.from_documents(
        client_settings=chroma_settings,
        documents=splits,
        embedding=ollamaEmbed
    )

    # 2. Wrap the resume document in a retriever tool
    retriever_tool = create_retriever_tool(
        resume_vectorstore.as_retriever(),
        "ResumeDocument",
        "A resume for the applicant"
    )
    return retriever_tool, docs
