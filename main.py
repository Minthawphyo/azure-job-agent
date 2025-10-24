import os
from dotenv import load_dotenv
from azure.identity import AzureCliCredential
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, ToolSet
from scraper_tool import scrape_jobs

# Load environment variables
load_dotenv()

# Auth via Azure CLI
credential = AzureCliCredential()

# Initialize client
client = AgentsClient(
    endpoint=os.getenv("PROJECT_ENDPOINT"),
    credential=credential
)

# Register scraper tool
scraper_tool = FunctionTool(
    name="scrape_jobs",
    description="Scrape job listings from Indeed using keyword and location.",
    function=scrape_jobs
)
tools = ToolSet([scraper_tool])

# Create the agent
agent = client.agents.create_agent(
    model=os.getenv("MODEL_DEPLOYMENT_NAME"),
    name="JobScraperAgent",
    instructions="You are an assistant that finds and summarizes job postings.",
    toolset=tools
)

# Ask it to scrape
response = client.agents.complete(
    agent_id=agent.id,
    messages=[
        {"role": "user", "content": "Find Python developer jobs in Singapore"}
    ]
)

print("\n--- Response ---")
print(response.output_text)
