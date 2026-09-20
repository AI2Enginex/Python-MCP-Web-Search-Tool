import asyncio
import os

from dotenv import load_dotenv
from fastmcp import Client

from google import genai
from google.genai import types
from mcp_servers.system_prompts import instructions

# load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")

# Initialize the Gemini client with the API key
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# If the MCP server path is not set in the environment, default to "src/mcp_servers/servers.py"
MCP_SERVER_PATH = os.getenv("MCP_SERVER_PATH", "src/mcp_servers/servers.py")

# If the model name is not set in the environment, default to "gemini-3.5-flash"
MODEL_NAME = os.getenv("MODEL_NAME", "gemini-3.5-flash")

# Function to convert an MCP Tool definition into a Gemini FunctionDeclaration.
# This function maps the MCP tool's name, description, and input schema to the corresponding Gemini format.
def convert_mcp_tool_to_gemini_tool(mcp_tool):
    """
    Convert an MCP Tool definition into a Gemini
    FunctionDeclaration.

    MCP provides something similar to:

        name
        description
        inputSchema

    Gemini expects:

        name
        description
        parameters
    """

    input_schema = mcp_tool.inputSchema

    # FastMCP/MCP schemas are generally Pydantic-like
    # objects or dictionaries depending on SDK version.
    if hasattr(input_schema, "model_dump"):
        input_schema = input_schema.model_dump()

    elif hasattr(input_schema, "dict"):
        input_schema = input_schema.dict()

    elif not isinstance(input_schema, dict):
        input_schema = dict(input_schema)

    return types.FunctionDeclaration(
        name=mcp_tool.name,
        description=mcp_tool.description or "",
        parameters=input_schema,
    )

# Function to convert all MCP tools into Gemini function declarations.
# These declarations are then used to inform the Gemini model about the available tools and their expected input formats.
def create_gemini_tools(mcp_tools):
    """
    Convert all MCP tools into Gemini function declarations.
    """
    # List to hold the converted Gemini function declarations
    function_declarations = list()

    # Iterate over each MCP tool, convert it to a Gemini function declaration, and add it to the list.
    for mcp_tool in mcp_tools:

        print(f"[CLIENT] Found MCP tool: {mcp_tool.name}")

        gemini_tool = convert_mcp_tool_to_gemini_tool(mcp_tool)

        function_declarations.append(gemini_tool)

    print(f"[CLIENT] Converted {len(function_declarations)} MCP tools into Gemini function declarations.")

    return types.Tool(
        function_declarations=function_declarations
    )


# Function to extract the result from an MCP CallToolResult into a format that Gemini can understand.
def extract_mcp_result(result):
    """
    Convert the MCP CallToolResult into something that
    Gemini can understand.

    FastMCP often provides structured data through
    result.data.

    For compatibility, we also inspect content.
    """
    # Check if the result has a 'data' attribute and if it's not None, return it directly.
    if hasattr(result, "data") and result.data is not None:
        return result.data

    
    # Check if the result has a 'structured_content' attribute and if it's not None, return it directly.
    if hasattr(result, "structured_content"):
        structured_content = result.structured_content

        if structured_content is not None:
            return structured_content

    
    # Check if the result has a 'content' attribute. 
    # If it does, extract the text from each item in the 
    # content and return it as a list or a single string.
    if hasattr(result, "content"):

        content = result.content

        output = list()

        for item in content:

            if hasattr(item, "text"):
                output.append(item.text)

            else:
                output.append(str(item))

        if len(output) == 1:
            return output[0]

        return output

    return str(result)


# Function to handle the complete lifecycle of a user question through MCP and Gemini.
async def chat_with_mcp(user_question: str):

    """
    Complete MCP + Gemini lifecycle.

    Flow:

        User
          ↓
        Gemini
          ↓
        Function Call
          ↓
        MCP Client
          ↓
        MCP Server
          ↓
        Tool Result
          ↓
        Gemini
          ↓
        Final Answer
    """

    # Connect to the MCP server using the specified path. The Client class manages the connection and communication with the MCP server.
    client = Client(MCP_SERVER_PATH)

    async with client:

        print("\n========================================")
        print("Connected to MCP Server")
        print("========================================\n")


        # List all available MCP tools from the server. This allows the Gemini model 
        # to know what tools it can call during the conversation.
        mcp_tools = await client.list_tools()

        print("[CLIENT] Available MCP tools:")

        for tool in mcp_tools:

            print(
                f"  - {tool.name}: "
                f"{tool.description}"
            )

        print()

        # Create Gemini tools from the MCP tools. This step converts the MCP tool definitions into a format 
        # that Gemini can understand, allowing it to call these tools as needed during the conversation.
        gemini_tool = create_gemini_tools(mcp_tools)

        # Create a configuration for the Gemini model, specifying the tools it can use, 
        # the system instructions, and other parameters like temperature and automatic function calling settings.
        config = types.GenerateContentConfig(
            tools=[gemini_tool],
            temperature=0,
            system_instruction=instructions(),
            automatic_function_calling=(
                types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            ),
        )

        # Prepare the initial content for the Gemini model, which includes the user's question. 
        # This content is structured in a way that Gemini can process and respond to.
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=user_question
                    )
                ],
            )
        ]
        print("========================================")
        print("Sending question to Gemini...")
        print("========================================\n")

        # Send the user's question to the Gemini model and receive a response.
        response = gemini_client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=config,
        )

        while True:

            function_calls = list()

            for part in response.candidates[0].content.parts:

                if part.function_call:

                    function_calls.append(part.function_call)

            # When Gemini does not request any tools, it means that it has enough information to provide 
            # a final answer to the user's question. In this case, we print the final answer and return it.
            if not function_calls:

                print("\n========================================")
                print("FINAL ANSWER")
                print("========================================\n")
                print(response.text)
                return response.text

            # When Gemini requests one or more tools, we print the requested tools and their arguments.
            print("\n========================================")
            print("Gemini requested MCP tool(s)")
            print("========================================\n")

            # Add the Gemini response to the conversation history. This allows Gemini to see its own 
            # request for tools in the context of the conversation.
            contents.append(
                response.candidates[0].content
            )


            # When Gemini requests tools, we prepare to call the requested MCP tools. 
            # We create a list to hold the results of these tool calls, which will be 
            # sent back to Gemini for further processing. 
            function_response_parts = list()

            for function_call in function_calls:

                tool_name = function_call.name

                tool_arguments = dict(function_call.args)

                print(f"[GEMINI] Tool: {tool_name}")

                print(f"[GEMINI] Arguments: "f"{tool_arguments}")

                # Check whether MCP tool exists before calling it. If the tool does not exist, 
                # we prepare an error message to send back to Gemini.
                available_tool_names = {tool.name for tool in mcp_tools}

                if tool_name not in available_tool_names:

                    tool_result = {
                        "error": (
                            f"Unknown MCP tool: "
                            f"{tool_name}"
                        )
                    }

                else:

                    try:
                        # Call the requested MCP tool with the provided arguments. The result of this call is then 
                        # extracted and prepared to be sent back to Gemini.
                        mcp_result = await client.call_tool(tool_name,tool_arguments,)

                        # Extract the result from the MCP tool call into a format that Gemini can understand. 
                        # This step ensures that the data returned from the MCP tool is compatible with Gemini's expected input format.
                        tool_result = extract_mcp_result(mcp_result)
                        print(f"[MCP] Result: {tool_result}")
                        

                    except Exception as e:

                        tool_result = {
                            "error": str(e)
                        }

                        print(
                            f"[MCP] Tool failed: "
                            f"{e}"
                        )


                # Gemini expects the results of tool calls to be structured in a specific way.
                # We create a Part for each tool result, which includes the tool's name and the 
                # result of the tool call. This Part is then added to the list of function response parts 
                # that will be sent back to Gemini.

                function_response_part = (
                    types.Part.from_function_response(
                        name=tool_name,

                        response={
                            "result": tool_result
                        },
                    )
                )

                function_response_parts.append(
                    function_response_part
                )

            # Add the results of the MCP tool calls to the conversation history. 
            # This allows Gemini to see the results of its requested tools in the 
            # context of the conversation, enabling it to make further decisions or provide a 
            # final answer based on this new information.
            contents.append(
                types.Content(
                    role="user",
                    parts=function_response_parts,
                )
            )


            print("\n========================================")
            print("Sending MCP result(s) back to Gemini...")
            print("========================================\n")


            # As we loop back to Gemini, we send the updated conversation history, 
            # which now includes the results of the MCP tool calls.

            response = gemini_client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config,
            )

            # Loop continues.
            #
            # Gemini can:
            #
            # 1. Request another tool
            #
            # OR
            #
            # 2. Produce the final answer.
            #
            # This is what enables multi-step tool calling.


# Main Entry Point for the MCP + Gemini Chatbot. This function handles user input, 
# manages the conversation loop, and calls the chat_with_mcp function to process each user question.
async def main(): # Main entry point for the MCP + Gemini Chatbot

    print("\n")
    print("========================================")
    print("      MCP + GEMINI CHATBOT")
    print("========================================")
    print()

    while True:

        user_question = input("You: ").strip()

        if user_question.lower() in {
            "exit",
            "quit",
            "q",
        }:

            print(
                "\nGoodbye!"
            )

            break

        if not user_question:
            continue

        try:

            await chat_with_mcp(user_question)

        except Exception as e:

            print(f"\nERROR: {e}\n")


# Run the application if this script is executed directly. This allows the chatbot to be started from the command line.
# The asyncio.run() function is used to run the main() coroutine, which manages the chatbot's conversation loop and handles user input.
# This is the entry point for the MCP + Gemini chatbot application.
if __name__ == "__main__":

    asyncio.run(main())

