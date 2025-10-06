import asyncio
import uuid
from rich.console import Console

from langchain_core.messages import HumanMessage

from chatagent.custom_graph import graph_builder


async def main():
    console = Console()
    graph = graph_builder.compile()
    provider_id = "fed1ce49-a55f-4ae9-ae1a-2b5823c020df"
    thread_id = str(uuid.uuid4())

    thread_cfg = {
        "configurable": {"thread_id": thread_id, "user_id": provider_id},
        "recursion_limit": 250,
    }

    console.print("Welcome to the Chat Agent! Type 'quit' to exit.", style="bold green")

    while True:
        try:
            user_input = console.input("You: ")
            if user_input.lower() == "quit":
                break

            state = {
                "messages": [HumanMessage(content=user_input)],
                "provider_id": provider_id,
                "input": user_input,
            }

            async for chunk in graph.astream(state, thread_cfg, stream_mode=["updates", "custom"]):
                stream_type, stream_data = chunk
                node_name = next(iter(stream_data.keys()))
                if node_name == "__interrupt__":
                    console.print(f"Agent needs input: {stream_data[node_name][0].value['data']['title']}", style="bold yellow")
                    human_response = console.input("Your response: ")
                    # This part is a bit tricky as we need to resume the graph with the human response.
                    # The following is a simplified way to resume, but a more robust solution might be needed
                    # depending on the exact interruption handling logic of the graph.
                    state = {
                        "messages": [HumanMessage(content=human_response)],
                        "provider_id": provider_id,
                        "input": human_response,
                    }

                else:
                    if "messages" in stream_data[node_name]:
                        for message in stream_data[node_name]["messages"]:
                            if hasattr(message, 'content') and message.content:
                                console.print(f"Agent: {message.content}", style="cyan")

        except KeyboardInterrupt:
            break

    console.print("Goodbye!", style="bold green")

if __name__ == "__main__":
    asyncio.run(main())