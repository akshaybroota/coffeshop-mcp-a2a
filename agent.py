from dotenv import load_dotenv
import logging
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
import os

load_dotenv
os.environ["GOOGLE_API_KEY"] = "<YOUR GOOGLE API KEY>"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a helpful assistant for a coffee shop. Your tasks include:

1. Using the MCP tools to get information about coffee items served, specific information about a coffee item and reserve a spot
2. Answering customer queries about coffee items, prices, and reservations
3. Providing accurate and helpful responses based on the information retrieved from the MCP tools
Please follow the guidelines and provide accurate information to customers. Be polite and helpful

"""
class CoffeeAgent:
    def __init__(self):
        logger.info("Loading MCP Tools from the MCP server...")
        toolset = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=("https://coffee-shop-mcp-us3xiidh7q-uc.a.run.app/mcp-server/mcp")
            ),
        )
        logger.info("MCP Tools loaded successfully.")
        self.agent =Agent(
            model="gemini-2.5-flash",
            name="CoffeeAgent",
            description="An agent that helps run the coffee shop.",
            instruction=SYSTEM_PROMPT,
            tools=[toolset],
        )

    def get_agent(self):
        """Returns the LlmAgent object."""
        return self.agent
