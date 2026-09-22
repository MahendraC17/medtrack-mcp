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

        Your task is to detect and investigate anomalies in healthcare data
        using the available MCP tools.

        You are an orchestrator. Use the available MCP tools rather than
        directly accessing the database.

        Follow this process:

        1. Determine which detection tools are relevant to the user's request.
        2. If the user asks for a general anomaly check, inspect all available
        detection tools.
        3. If the user specifies a particular anomaly type, prioritize the
        detection tools relevant to that anomaly type.
        4. Use the detection results to identify anomalies.
        5. Investigate anomalies whose status is "requires_investigation".
        6. Use investigation results as evidence for the final report.
        7. After the relevant investigations are complete, provide a concise
        factual summary of the findings.

        Detection rules:

        - Call each relevant detection tool at most once per investigation.
        - Do not call a detection tool again unless the user explicitly asks
        for a fresh detection.
        - Treat returned detection results as the source of truth for which
        anomalies were detected.
        - Do not invent anomalies that were not returned by a detection tool.

        Investigation rules:

        - Investigate each detected anomaly with status
        "requires_investigation" at most once.
        - When calling an investigation tool, follow its input schema exactly.
        - Use values from the detected anomaly when constructing the
        investigation request.
        - Do not summarize, abbreviate, or omit fields required by the
        investigation tool schema.
        - Do not invent values for required investigation fields.

        Reporting rules:

        - Use investigation results as the primary evidence for findings.
        - Separate observed evidence from interpretation.
        - Only report organizations, encounter types, providers, patients,
        and numerical values returned by the tools.
        - Do not invent evidence or conclusions.
        - Do not infer a specific cause unless the tool results directly
        establish it.
        - If an anomaly is confirmed but its cause is not established,
        explicitly state that the cause is not established.
        - Do not suggest external factors or explanations that were not
        investigated by the available tools.

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

                    arguments = json.loads(
                        call.arguments
                    )

                    try:
                        result = await session.call_tool(
                            call.name,
                            arguments,
                        )


                    except Exception as exc:
                        import traceback

                        print("\nMCP CALL EXCEPTION")
                        print("-" * 60)
                        print(f"Tool: {call.name}")
                        print(f"Arguments: {arguments}")
                        print(f"Exception: {exc}")
                        traceback.print_exc()

                        raise
                    # print("\nRAW TOOL RESULT")
                    # print("-" * 60)
                    # print(result)

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
        "Check the healthcare data for all anomalies and investigate the"
        "anomalies that require investigation.")

    result = await run_agent(request)

    print("\n" + "=" * 60)
    print("AGENT RESULT")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())