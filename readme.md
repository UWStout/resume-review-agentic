# Resume Review Agent (2026)
This is an updated tool that will review resumes and provide feedback on how to improve them. It utilizes a locally installed and running LLM AI tool and an agentic RAG with modern (as of 2026) embedding and instruct LLMs.

## Libraries & Tools Used
This is a brief overview of the languages, libraries, and tools involved in this agent:
- It is written in Python employing the LangChain/LangGraph library.
- It uses a local instance of the Unstructured.io PDF parser (you will need a free API key)
- It uses LLMs running locally via Ollama (you must setup and install the LLMs yourself)
- It employs the Chroma Vector Store which is free to use (for personal projects)

You will need some familiarity with Ollama to use this project as is. However, it should not be difficult to update the tool to use a cloud based LLM. You will need your own API keys for these LLMs and you should be careful not to upload those to a github repository. Also, you will likely need to spend tokens and pay for access to these services (if you want an LLM that will do a decent job). Explore LangChain's community providers and swap out my use of the Ollama providers for you cloud providers as you see fit.

## Prerequisites
You will need a locally installed instance of Ollama with a good embedding and instruct LLM. To run in a reasonable time, it will require a decent GPU with significant amounts of VRAM (>10GB).

The current system also utilizes an local instance of Unstructured.io's PDF parser. I opted to create a docker container on my local machine as this was much cleaner than installing and running the full unstructured tool locally.

The docker-compose.yaml file in the root will setup the unstructured.io container for you. If you have docker desktop installed, just run `docker compose up -d` to use this existing docker file. I use port 5000 instead of the often overcrowded 8000. It also attempts to read your unstructured.io API key from the .env file so you should create that file FIRST (see below).

## Setup & Usage
Once the prerequisites are satisfied, start by creating a .env file with the following parameters:
```ini
# Unstructured IO info (I recommend the local docker container approach)
UNSTRUCTURED_API_KEY=your_personal_unstructured_api_key
UNSTRUCTURED_CUSTOM_HOST=ip_of_local_unstructured_instance_or_localhost
UNSTRUCTURED_CUSTOM_PORT=port_of_local_unstructured_instance

# Info about your local Ollama server
OLLAMA_CUSTOM_HOST=localhost_or_ip_of_host
OLLAMA_CUSTOM_PORT=port_of_host

# Names of the models you wish to use (must be installed in Ollama already)
EMBEDDING_MODEL_NAME=name_of_embedding_model_LLM
AGENT_MODEL_NAME=name_of_instruct_LLM
```

With all of these things in place, execute the following:
- Run `bootstrap_env.sh` for bash or `bootstrap_env.bat` for windows
  * This creates a python venv and installs required dependencies
- Place your resume PDFs in the `input` folder
- Run `python resume_agent.py`
- The results will be in the `output` folder
