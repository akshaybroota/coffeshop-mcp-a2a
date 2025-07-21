import json
import logging

from typing import Any
from uuid import uuid4

import httpx

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)


async def main() -> None:
    PUBLIC_AGENT_CARD_PATH = '/.well-known/agent.json'
    EXTENDED_AGENT_CARD_PATH = '/agent/authenticatedExtendedCard'

    # Configure logging to show INFO level messages
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)  # Get a logger instance

    # --8<-- [start:A2ACardResolver]

    base_url = 'https://coffee-shop-a2a-server-378244746088.us-central1.run.app'

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
            # agent_card_path uses default, extended_agent_card_path also uses default
        )
        # --8<-- [end:A2ACardResolver]

        # Fetch Public Agent Card and Initialize Client
        final_agent_card_to_use: AgentCard | None = None

        try:
            logger.info(
                f'Attempting to fetch public agent card from: {base_url}{PUBLIC_AGENT_CARD_PATH}'
            )
            _public_card = (
                await resolver.get_agent_card()
            )  # Fetches from default public path
            logger.info('Successfully fetched public agent card:')
            logger.info(
                _public_card.model_dump_json(indent=2, exclude_none=True)
            )
            final_agent_card_to_use = _public_card
            logger.info(
                '\nUsing PUBLIC agent card for client initialization (default).'
            )

            if _public_card.supportsAuthenticatedExtendedCard:
                try:
                    logger.info(
                        f'\nPublic card supports authenticated extended card. Attempting to fetch from: {base_url}{EXTENDED_AGENT_CARD_PATH}'
                    )
                    auth_headers_dict = {
                        'Authorization': 'Bearer dummy-token-for-extended-card'
                    }
                    _extended_card = await resolver.get_agent_card(
                        relative_card_path=EXTENDED_AGENT_CARD_PATH,
                        http_kwargs={'headers': auth_headers_dict},
                    )
                    logger.info(
                        'Successfully fetched authenticated extended agent card:'
                    )
                    logger.info(
                        _extended_card.model_dump_json(
                            indent=2, exclude_none=True
                        )
                    )
                    final_agent_card_to_use = (
                        _extended_card  # Update to use the extended card
                    )
                    logger.info(
                        '\nUsing AUTHENTICATED EXTENDED agent card for client initialization.'
                    )
                except Exception as e_extended:
                    logger.warning(
                        f'Failed to fetch extended agent card: {e_extended}. Will proceed with public card.',
                        exc_info=True,
                    )
            elif (
                _public_card
            ):  # supportsAuthenticatedExtendedCard is False or None
                logger.info(
                    '\nPublic card does not indicate support for an extended card. Using public card.'
                )

        except Exception as e:
            logger.error(
                f'Critical error fetching public agent card: {e}', exc_info=True
            )
            raise RuntimeError(
                'Failed to fetch the public agent card. Cannot continue.'
            ) from e

    # --8<-- [start:cli_interaction]
        client = A2AClient(
            httpx_client=httpx_client, agent_card=final_agent_card_to_use
        )
        logger.info('A2AClient initialized.')

        print("Type your message and press Enter. Type 'exit' to quit.")
        while True:
            user_input = input('You: ')
            if user_input.strip().lower() in {'exit', 'quit'}:
                print('Exiting.')
                break
            if not user_input.strip():
                continue
            send_message_payload: dict[str, Any] = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': user_input}
                    ],
                    'messageId': uuid4().hex,
                },
            }
            request = SendStreamingMessageRequest(
                id=str(uuid4()), params=MessageSendParams(**send_message_payload)
            )
            # Print without newline, flush immediately
            # print('Agent: ', end='', flush=True)

            response = client.send_message_streaming(request)
            has_received_data = False
            async for chunk in response:
                data = json.loads(chunk.model_dump_json(
                    indent=2, exclude_none=True))
                has_received_data = True
                if (
                    "result" in data
                    and "artifact" in data["result"]
                    and "parts" in data["result"]["artifact"]
                    and len(data["result"]["artifact"]["parts"]) > 0
                    and "text" in data["result"]["artifact"]["parts"][0]
                ):

                    extracted_message = data["result"]["artifact"]["parts"][0]["text"]
                    # For debugging
                    print(f"CoffeShopAgent: {extracted_message.strip()}")

        # Check for the final 'completed' status to stop processing
                if (
                    "result" in data
                    and "final" in data["result"]
                    and data["result"]["final"] is True
                    and "status" in data["result"]
                    and "state" in data["result"]["status"]
                    and data["result"]["status"]["state"] == "completed"
                ):
                    # print("Received final 'completed' chunk. Stopping.") # For debugging
                    break  # Exit the loop as the stream is complete
            if not has_received_data:
                logger.warning("No data received from the agent.")
            print()

if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
