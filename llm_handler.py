from getpass import getpass
from langchain_community.chat_models import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.llms import Ollama

def get_llm():
    print("\nChoose LLM type: (1) Local LLM or (2) Online API Key:", end=" ")
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
    else:
        print("❌ Invalid choice.")
        exit(1)
        
    return llm, model_name




'''from getpass import getpass
import google.generativeai as genai

def get_llm():
    print("\nChoose LLM type: (1) Local LLM or (2) Online API Key:", end=" ")
    choice = input().strip()

    if choice == "2":
        provider = input("Enter online LLM provider (e.g., openai, google, openrouter, groq): ").strip().lower()
        model = input("Enter model name (e.g., gpt-4, gemini-1.5-pro, gemini-2.5-flash): ").strip()
        key = getpass("Enter API key (will be hidden): ")

        if provider == "openai":
            from langchain_community.chat_models import ChatOpenAI
            return ChatOpenAI(model_name=model, openai_api_key=key)

        elif provider == "google":
            genai.configure(api_key=key)
            return genai.GenerativeModel(model)

        elif provider == "openrouter":
            from langchain_community.chat_models import ChatOpenAI
            return ChatOpenAI(
                model_name=model,
                openai_api_key=key,
                openai_api_base="https://openrouter.ai/api/v1"
            )

        elif provider == "groq":
            from langchain_community.chat_models import ChatOpenAI
            return ChatOpenAI(
                model_name=model,
                openai_api_key=key,
                openai_api_base="https://api.groq.com/openai/v1"
            )

        else:
            raise ValueError("❌ Unsupported provider.")

    else:
        print("❌ Local LLM not yet supported.")
        exit(1)
'''


'''from getpass import getpass
from langchain_community.chat_models import ChatOpenAI, ChatGooglePalm

def get_llm():
    print("\nChoose LLM type: (1) Local LLM or (2) Online API Key:", end=" ")
    choice = input().strip()

    if choice == "2":
        provider = input("Enter online LLM provider (e.g., openai, google, openrouter, groq): ").strip().lower()
        model = input("Enter model name (e.g., gpt-4, gemini-pro, mistral, llama3): ").strip()
        key = getpass("Enter API key (will be hidden): ")

        if provider == "openai":
            return ChatOpenAI(model_name=model, openai_api_key=key)

        elif provider == "google":
            return ChatGooglePalm(model=model, google_api_key=key)

        elif provider == "openrouter":
            return ChatOpenAI(
                model_name=model,
                openai_api_key=key,
                openai_api_base="https://openrouter.ai/api/v1"
            )

        elif provider == "groq":
            return ChatOpenAI(
                model_name=model,
                openai_api_key=key,
                openai_api_base="https://api.groq.com/openai/v1"
            )

        else:
            raise ValueError("❌ Unsupported provider.")

    else:
        # TODO: Replace this with actual local LLM class
        print("❌ Local LLM not yet supported.")
        exit(1)
'''
