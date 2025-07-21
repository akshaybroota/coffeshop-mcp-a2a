import logging
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent import CoffeeAgent
from agent_executor import CoffeShopAgentExecutor
from google.adk.agents import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
import uvicorn

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

PUBLIC_URL = "https://coffee-shop-a2a-server-378244746088.us-central1.run.app"


class CoffeShopAgentServer:

    def __init__(self):
        self.agent = self._build_agent()
        self.task_store = InMemoryTaskStore()
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()
        self.memory_service = InMemoryMemoryService()

        self.runner = Runner(
            app_name="CoffeeShopAgent",
            agent=self.agent,
            session_service=self.session_service,
            artifact_service=self.artifact_service,
            memory_service=self.memory_service
        )
        capabilities = AgentCapabilities(streaming=True)
        skill = AgentSkill(
            id="coffee_shop_skill",
            name="CoffeeShopAgentSkill",
            description="""Skill for managing coffee shop operations.""",
            tags=["coffee shop management"],
            examples=[
                "Which coffees do you sell?",
                "What is the cost of an Americano?",
                "Can you book a reservation for me?",
            ]
        )
        self.agent_card = AgentCard(
            name="Coffee Shop Agent",
            description="An agent that helps run the coffee shop.",
            url=PUBLIC_URL,
            version="1.0.0",
            defaultInputModes=["text", "text/plain"],
            defaultOutputModes=["text", "text/plain"],
            capabilities=capabilities,
            skills=[skill],
        )

    def _build_agent(self) -> LlmAgent:
        return CoffeeAgent().get_agent()


# --- Cloud Run Entrypoint ---
if __name__ == "__main__":
    try:
        logger.info("Starting Coffee Shop Agent server...")
        # Initialize the CoffeeAgent
        coffee_shop_agent_server = CoffeShopAgentServer()
        # Create the request handler
        request_handler = DefaultRequestHandler(
            agent_executor=CoffeShopAgentExecutor(
                coffee_shop_agent_server.agent, coffee_shop_agent_server.runner),
            task_store=InMemoryTaskStore(),
        )
        # Create the A2A Starlette app
        server = A2AStarletteApplication(
            agent_card=coffee_shop_agent_server.agent_card,
            http_handler=request_handler,
        )
        # Run the server with uvicorn
        uvicorn.run(server.build(), host="0.0.0.0", port=8080)
        logger.info("Coffee Shop Agent server started successfully.")
    except Exception as e:
        logger.exception(f"Failed to start the Coffee Shop Agent server: {e}")
        exit(1)
