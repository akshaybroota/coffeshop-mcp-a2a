import logging
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import TaskState, TextPart, UnsupportedOperationError
from a2a.utils import new_agent_text_message
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.genai import types


class CoffeShopAgentExecutor(AgentExecutor):
    def __init__(self, agent: LlmAgent, runner: Runner):
        self.agent = agent
        self.runner = runner

    async def execute(self, context, event_queue):
        logging.info("Executing Coffee Shop Agent task...")

        query = context.get_user_input()

        updater = TaskUpdater(event_queue, context.task_id, context.context_id)

        if not context.current_task:
            await updater.submit()

        await updater.start_work()

        content = types.Content(role='user', parts=[types.Part(text=query)])
        user_id = "123"
        session = await self.runner.session_service.get_session(
            app_name=self.runner.app_name,
            user_id=user_id,
            session_id=context.context_id,
        ) or await self.runner.session_service.create_session(
            app_name=self.runner.app_name,
            user_id=user_id,
            session_id=context.context_id,
        )

        try:
            async for event in self.runner.run_async(
                    session_id=session.id, user_id="123", new_message=content):
                logging.info(f"Received event: {event}")
                if event.is_final_response():
                    parts = event.content.parts
                    text_parts = [TextPart(text=part.text) for part in parts]
                    await updater.add_artifact(
                        text_parts,
                        name="result",
                    )
                    await updater.complete()
                    break
                await updater.update_status(
                    TaskState.working, message=new_agent_text_message(
                        "working....")
                )
            else:
                logging.error(
                    "Agent async run failed: No final response received.")
                await updater.update_status(TaskState.failed, message=new_agent_text_message("Failed to generate any message."))
        except Exception as e:
            logging.exception(f"Error during agent execution: {e}")
            await updater.update_status(TaskState.failed, message=new_agent_text_message("Agent execution error."))

    async def cancel(self, context, event_queue):
        logging.info("Canceling Coffee Shop Agent task...")