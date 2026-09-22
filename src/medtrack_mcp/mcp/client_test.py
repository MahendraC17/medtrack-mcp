import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

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

            tools = await session.list_tools()

            print("\nAVAILABLE TOOLS")
            print("-" * 60)

            for tool in tools.tools:
                print(tool.name)

            # MT 001
            result = await session.call_tool(
                "detect_encounter_volume_anomalies_tool",
                {},
            )

            print("\nDETECTION RESULT")
            print("-" * 60)
            print(result)

            anomaly_events = [
                json.loads(content.text)
                for content in result.content
            ]

            for anomaly_event in anomaly_events:

                investigation_result = await session.call_tool(
                    "investigate_encounter_volume_tool",
                    {
                        "request": {
                            "anomaly_type": anomaly_event["anomaly_type"],
                            "metric": anomaly_event["metric"],
                            "period_start": anomaly_event["period_start"],
                            "period_end": anomaly_event["period_end"],
                            "period": anomaly_event["period"],
                        }
                    },
                )

                print("\nMT-001 INVESTIGATION RESULT")
                print("-" * 60)
                print(investigation_result)

            # MT 002
            result = await session.call_tool(
                "detect_patient_encounter_frequency_anomalies_tool",
                {},
            )

            print("\nMT-002 DETECTION RESULT")
            print("-" * 60)
            print(result)

            anomaly_events = [
                json.loads(content.text)
                for content in result.content
            ]

            for anomaly_event in anomaly_events:

                investigation_result = await session.call_tool(
                    "investigate_patient_encounter_frequency_tool",
                    {
                        "request": {
                            "anomaly_type": anomaly_event["anomaly_type"],
                            "metric": anomaly_event["metric"],
                            "patient_id": anomaly_event["patient_id"],
                            "period_start": anomaly_event["period_start"],
                            "period_end": anomaly_event["period_end"],
                            "period": anomaly_event["period"],
                            "observed_value": anomaly_event["observed_value"],

                        }
                    },
                )

                print("\nMT-002 INVESTIGATION RESULT")
                print("-" * 60)
                print(investigation_result)

            for item in result.content:
                print("\nCONTENT:")
                print(item)


if __name__ == "__main__":
    asyncio.run(main())