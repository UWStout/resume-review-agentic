# Standard libraries
from os import getenv

# For creating the agent
from langchain.agents import create_agent
from langchain_ollama import ChatOllama

# Read environment variable secrets
from dotenv import load_dotenv
load_dotenv()

OLLAMA_HOST = getenv("OLLAMA_CUSTOM_HOST", "localhost")
OLLAMA_PORT = getenv("OLLAMA_CUSTOM_PORT", "11434")
AGENT_MODEL_NAME = getenv("AGENT_MODEL_NAME", "qwen2.5:7b-instruct")

# Our resume system prompt
system_prompt = """
You are a concise assistant. Provide direct answers, minimize conversational filler, and focus only on the requested
information. Use ONLY the provided ResumeDocument tool to answer questions. If the answer cannot be found in the tool
ResumeDocument, say you do not know. Do not use external knowledge. Do not fix the ResumeDocument or provide examples of
a more complete or better structured ResumeDocument. Be brief and just answer the questions asked.

The ResumeDocument represents the resume of a college student that is seeking either an internship or a full-time job.
It should be short and professional. Please refer to the applicant with they/them pronouns and avoid using gendered language.
Please utilize the Markdown language in your response to style any text and make sure your response is compatible with the
Markdown language.

The ResumeRules tool provides facts about a strong and complete resume. A good resume should have the qualities
described in ResumeRules. When evaluating this resume, use only the rules that are specified in ResumeRules.

Do not use tools from a previous search. Use only tools supplied from this current conversation. Do not use any conversation
history from a previous user chat. Use only the history from this user conversation.
"""

def create_resume_agent(resume_tools, agent_temp=0.1):
    # 3. Setup Agent
    agent_llm = ChatOllama(model=AGENT_MODEL_NAME, temperature=agent_temp, base_url=f"http://{OLLAMA_HOST}:{OLLAMA_PORT}")
    return create_agent(
        agent_llm,
        tools=[*resume_tools],
        system_prompt=system_prompt
    )

def query_resume_agent(questions, agent_runnable, unique_id):
    # Build user messages from questions
    user_messages = [{ "role": "user", "content": question } for question in questions]

    # Run queries and gather responses
    responses = []
    for user_message in user_messages:
        response = agent_runnable.invoke({ "messages": user_message }, { "configurable": { "thread_id": unique_id } })
        AIMessages = [item.text for item in response['messages'] if getattr(item, "type", None) == "ai" and item.text.strip() != ""]
        responses.append(AIMessages)

    # Return the responses
    return responses
