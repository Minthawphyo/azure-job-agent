import os
from dotenv import load_dotenv
from typing import Any
from pathlib import Path
from azure.identity import DefaultAzureCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet, MessageRole, ListSortOrder
from scraper_tool import scrap_functions  # <- { scrape_jobs }

def main():
    # Clear console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Load environment variables
    load_dotenv()
    project_endpoint = os.getenv("PROJECT_ENDPOINT")
    model_deployment = os.getenv("MODEL_DEPLOYMENT_NAME")

    if not project_endpoint or not model_deployment:
        print("❌ Missing PROJECT_ENDPOINT or MODEL_DEPLOYMENT_NAME in .env file.")
        return

    # Connect to Azure Agent client
    agent_client = AgentsClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        )
    )

    with agent_client:
        # Define agent and tools
        functions = FunctionTool(scrap_functions)
        toolset = ToolSet()
        toolset.add(functions)
        agent_client.enable_auto_function_calls(toolset)

        agent = agent_client.create_agent(
            model=model_deployment,
            name="JobScraperAgent",
            instructions="You are a helpful assistant that can find and summarize job postings.",
            toolset=toolset
        )

        thread = agent_client.threads.create()
        print(f"\n🤖 You're now chatting with: {agent.name} ({agent.id})")
        print("Type your question or type 'quit' to exit.\n")

        try:
            while True:
                user_prompt = input("You: ")
                if user_prompt.lower() == "quit":
                    print("Goodbye! 👋")
                    break
                if len(user_prompt.strip()) == 0:
                    print("Please enter a prompt.")
                    continue

                # Send user message
                agent_client.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=user_prompt
                )

                # Run agent
                run = agent_client.runs.create_and_process(
                    thread_id=thread.id,
                    agent_id=agent.id
                )

                if run.status == "failed":
                    print(f"⚠️ Run failed: {run.last_error}")
                    continue

                # Display assistant reply
                last_msg = agent_client.messages.get_last_message_text_by_role(
                    thread_id=thread.id,
                    role=MessageRole.AGENT
                )
                if last_msg:
                    print(f"\n{agent.name}: {last_msg.text.value}\n")

        except KeyboardInterrupt:
            print("\n\n👋 Chatbot stopped by user. Exiting cleanly...")

        # Conversation log
        print("\n📜 Conversation Log:\n")
        messages = agent_client.messages.list(
            thread_id=thread.id,
            order=ListSortOrder.ASCENDING
        )
        for msg in messages:
            if msg.text_messages:
                text_value = msg.text_messages[-1].text.value
                print(f"{msg.role}: {text_value}\n")

if __name__ == '__main__':
    main()
