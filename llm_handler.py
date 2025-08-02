from getpass import getpass
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama

def get_llm():
    print("\nChoose LLM type: (1) Local LLM, (2) Online API Key, or (3) Local Tools (No LLM):", end=" ")
    choice = input().strip()
    model_name = ""
    llm = None

    if choice == "1":
        model_name = input("Enter local model name (e.g., llama2, mistral): ").strip()
        llm = Ollama(model=model_name)

    elif choice == "2":
        provider = input("Enter online LLM provider (e.g., openai, google, openrouter, groq): ").strip().lower()
        model_name = input("Enter model name (e.g., gpt-4, gemini-1.5-pro): ").strip()
        key = getpass("Enter API key (will be hidden): ")

        if provider == "openai":
            llm = ChatOpenAI(model_name=model_name, openai_api_key=key)
        elif provider == "google":
            llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=key)
        elif provider in ["openrouter", "anthropic", "meta-llama", "mistral", "llama3", "claude"]:
            llm = ChatOpenAI(
                model_name=model_name,
                openai_api_key=key,
                openai_api_base="https://openrouter.ai/api/v1"
            )
        elif provider == "groq":
            llm = ChatOpenAI(
                model_name=model_name,
                openai_api_key=key,
                openai_api_base="https://api.groq.com/openai/v1"
            )
        else:
            print("❌ Unsupported provider.")
            exit(1)
            
    elif choice == "3":
        return None, "local_tools"
        
    else:
        print("❌ Invalid choice.")
        exit(1)
        
    return llm, model_name
