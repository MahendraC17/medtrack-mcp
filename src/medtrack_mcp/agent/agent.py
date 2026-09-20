import asyncio
import json
import os
from dotenv import load_dotenv

from openai import OpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
load_dotenv()

MODEL = "gpt-4.1-nano-2025-04-14"

SYSTEM_PROMPT = """
You are a healthcare data investigation agent.

Your task is to detect and investigate anomalies in the healthcare
data using the available MCP tools.

Follow this process:

1. Use the detection tool to identify anomalies.
2. Investigate anomalies whose status requires investigation.
3. Use the investigation results as evidence.
4. Provide a concise factual summary of what was detected and what
   the investigation found.
5. Do not invent evidence or conclusions that are not supported by
   the tool results.

You are an orchestrator. Use the available tools rather than directly
accessing the database.

When reporting findings:

- Separate observed evidence from interpretation.
- Only report organizations, encounter types, providers, patients,
  and numerical values returned by the investigation tool.
- Do not invent or infer specific organizations or causes.
- Do not claim to know the cause of an anomaly unless the tool
  results directly support it.
- If the evidence establishes that an anomaly exists but not why it
  occurred, explicitly state that the cause is not established.

  Tool-use rules:

- Call the detection tool once at the beginning of an investigation.
- Use the returned detection results as the source of truth for which
  anomalies require investigation.
- Do not call the detection tool again unless the user explicitly
  asks for a fresh detection.
- Investigate each anomaly with status "requires_investigation"
  at most once.
- After all relevant anomalies have been investigated, produce the
  final report.
"""


def get_openai_client():

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set."
        )

    return OpenAI(api_key=api_key)


def convert_mcp_tools(mcp_tools):

    tools = []

    for tool in mcp_tools:

        tools.append(
            {
                "type": "function",
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            }
        )

    return tools


def extract_tool_result(result):

    if result.is_error:
        return {
            "error": True,
            "content": [
                content.text
                for content in result.content
                if hasattr(content, "text")
            ],
        }

    content = []

    for item in result.content:

        if hasattr(item, "text"):

            try:
                content.append(
                    json.loads(item.text)
                )
            except json.JSONDecodeError:
                content.append(item.text)

    if len(content) == 1:
        return content[0]

    return content


async def run_agent(user_request):

    client = get_openai_client()

    server_params = StdioServerParameters(
        command="uv",
        args=[
            "run",
            "python",
            "-m",
            "medtrack_mcp.mcp.server",
        ],
    )

    async with stdio_client(server_params) as (
        read_stream,
        write_stream,
    ):

        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:

            await session.initialize()

            mcp_tools = await session.list_tools()

            tools = convert_mcp_tools(
                mcp_tools.tools
            )

            print("\nAVAILABLE MCP TOOLS")
            print("-" * 60)

            for tool in tools:
                print(tool["name"])

            response = client.responses.create(
                model=MODEL,
                instructions=SYSTEM_PROMPT,
                input=user_request,
                tools=tools,
            )

            while True:

                function_calls = [
                    item
                    for item in response.output
                    if item.type == "function_call"
                ]

                if not function_calls:
                    return response.output_text

                tool_outputs = []

                for call in function_calls:

                    print(
                        f"\nAGENT CALLING TOOL: "
                        f"{call.name}"
                    )

                    arguments = json.loads(
                        call.arguments
                    )

                    result = await session.call_tool(
                        call.name,
                        arguments,
                    )

                    tool_result = extract_tool_result(
                        result
                    )

                    tool_outputs.append(
                        {
                            "type": "function_call_output",
                            "call_id": call.call_id,
                            "output": json.dumps(
                                tool_result,
                                default=str,
                            ),
                        }
                    )

                response = client.responses.create(
                    model=MODEL,
                    instructions=SYSTEM_PROMPT,
                    input=tool_outputs,
                    tools=tools,
                    previous_response_id=response.id,
                )


async def main():

    request = (
        "Check the healthcare data for unusual encounter "
        "volume activity. Investigate any anomalies that "
        "require investigation and explain what you find."
    )

    result = await run_agent(request)

    print("\n" + "=" * 60)
    print("AGENT RESULT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())