# MCP Server with Gemini — Model Context Protocol Tool Calling

A practical implementation of **Model Context Protocol (MCP)** using Python, `uv`, and Google's Gemini API.

This project demonstrates the complete MCP lifecycle:

**User → Gemini LLM → Tool Selection → MCP Client → MCP Server → Tool Execution → Tool Result → Gemini → Final Response**

The goal of this project is to understand how an LLM can dynamically discover and use external tools through an MCP server rather than having tool implementations directly embedded inside the LLM application.

---

## 📌 Project Overview

Large Language Models are powerful at understanding natural language, but they do not inherently have access to external systems such as:

* APIs
* Databases
* Files
* Web services
* Internal enterprise systems
* Custom Python functions

MCP provides a standardized way for an AI application to communicate with external tools and data sources.

In this project:

1. An **MCP Server** exposes tools.
2. An **MCP Client** connects to the server.
3. The client retrieves the available tool definitions.
4. Gemini receives the tool definitions.
5. Gemini automatically determines whether a tool is required.
6. The client invokes the selected MCP tool.
7. The MCP server executes the tool.
8. The result is returned to the client.
9. The result is provided back to Gemini.
10. Gemini generates the final natural-language response.

---

# 🏗️ Architecture

```text
                         User
                           │
                           │ Natural Language Query
                           ▼
                  ┌─────────────────┐
                  │   Gemini LLM    │
                  │                 │
                  │ Tool Selection  │
                  └────────┬────────┘
                           │
                           │ Function / Tool Call
                           ▼
                  ┌─────────────────┐
                  │   MCP Client   │
                  │                 │
                  │ • Connects MCP  │
                  │ • Lists Tools   │
                  │ • Calls Tools   │
                  └────────┬────────┘
                           │
                           │ MCP Protocol
                           ▼
                  ┌─────────────────┐
                  │   MCP Server   │
                  │                 │
                  │ Tool Registry   │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Tool Function  │
                  │                 │
                  │ External Logic  │
                  └────────┬────────┘
                           │
                           │ Tool Result
                           ▼
                  ┌─────────────────┐
                  │   MCP Client   │
                  └────────┬────────┘
                           │
                           │ Tool Result
                           ▼
                  ┌─────────────────┐
                  │   Gemini LLM    │
                  │                 │
                  │ Final Response  │
                  └────────┬────────┘
                           │
                           ▼
                         User
```

---

# 🔄 Complete MCP Lifecycle

The implementation demonstrates the following lifecycle.

## 1. Start MCP Server

The MCP server exposes one or more tools.

For example:

```python
@mcp.tool()
def get_latest_news(company: str):
    ...
```

The MCP server does not decide when the tool should be used.

It simply exposes the capability.

---

## 2. MCP Client Connects to Server

The MCP client establishes a connection with the MCP server.

The client can then communicate with the server using the MCP protocol.

Conceptually:

```text
MCP Client
    │
    │ MCP
    ▼
MCP Server
```

---

## 3. Discover Available Tools

The client asks the MCP server for its available tools.

For example:

```text
Available Tools:

1. get_latest_news
   Description: Fetch latest news for a company

2. get_stock_price
   Description: Get the current stock price

3. calculate_sum
   Description: Add two numbers
```

The important point is that the client does not need to hard-code every tool.

The tools are discovered from the MCP server.

---

## 4. Send Tool Definitions to Gemini

The MCP client converts the discovered MCP tools into a format Gemini can understand as callable functions/tools.

Conceptually:

```text
MCP Tool Definition
        │
        ▼
Function Declaration
        │
        ▼
Gemini
```

Gemini receives information such as:

```text
Tool Name:
get_latest_news

Description:
Fetch the latest news for a company.

Parameters:
company: string
```

---

## 5. Gemini Automatically Selects a Tool

Suppose the user asks:

```text
Fetch the latest news for HDFC Bank.
```

Gemini determines that the `get_latest_news` tool is appropriate.

Instead of generating a normal answer, Gemini produces a tool call similar to:

```text
get_latest_news(
    company="HDFC Bank"
)
```

The important concept is:

> The LLM decides **which tool to use**, while the MCP server decides **how the tool is actually executed**.

---

# 🛠️ Tool Execution

The MCP client receives Gemini's tool-call request.

It then invokes the corresponding MCP tool.

```text
Gemini
   │
   │ get_latest_news("HDFC Bank")
   ▼
MCP Client
   │
   │ call_tool()
   ▼
MCP Server
   │
   │ Execute Python Function
   ▼
External API / Logic
```

The MCP server executes the actual function.

---

# 📤 Returning the Tool Result

After execution, the MCP server returns the result to the MCP client.

For example:

```text
[
    {
        "title": "HDFC Bank reports...",
        "url": "...",
        "summary": "..."
    }
]
```

The client then sends this result back to Gemini.

---

# 🤖 Final LLM Response

Gemini receives the tool result and generates the final response.

For example:

```text
Here are the latest HDFC Bank news updates:

1. HDFC Bank reported...
2. The bank announced...
3. Analysts expect...
```

Therefore, the complete flow becomes:

```text
User Query
    ↓
Gemini
    ↓
Tool Selection
    ↓
MCP Client
    ↓
MCP Server
    ↓
Tool Execution
    ↓
Tool Result
    ↓
MCP Client
    ↓
Gemini
    ↓
Final Answer
```

---

# 📁 Project Structure

A recommended project structure is:

```text
mcp-gemini-server/
│
├── src/
│   └── mcp_servers/
│       ├── __init__.py
│       └── ...
│
├── client.py
├── server.py
│
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml
└── uv.lock
```

### `server.py`

Contains the MCP server implementation and exposed tools.

Example:

```python
@mcp.tool()
def get_latest_news(company: str):
    ...
```

### `client.py`

Responsible for:

* Connecting to the MCP server
* Discovering tools
* Converting MCP tools into Gemini-compatible tool declarations
* Sending user queries to Gemini
* Processing Gemini tool calls
* Invoking MCP tools
* Sending tool results back to Gemini
* Generating the final response

### `pyproject.toml`

Defines project metadata and dependencies.

### `uv.lock`

Contains the resolved dependency versions used by the project.

### `.env`

Contains secrets such as API keys.

This file should **never be committed to GitHub**.

### `.env.example`

Contains the required environment variables without exposing actual secrets.

---

# 🐍 Technology Stack

| Technology  | Purpose                                  |
| ----------- | ---------------------------------------- |
| Python 3.12 | Application development                  |
| MCP         | Standardized tool communication          |
| Gemini API  | LLM and tool selection                   |
| `uv`        | Python project and dependency management |
| asyncio     | Asynchronous MCP communication           |
| dotenv      | Environment variable management          |
| Git/GitHub  | Version control                          |

---

# 📦 Why `uv`?

This project uses `uv` instead of managing the environment manually with `pip` and `venv`.

`uv` provides:

* Fast dependency installation
* Virtual environment management
* Dependency resolution
* Lock file generation
* Reproducible environments
* Convenient project execution

The important files are:

```text
pyproject.toml
uv.lock
```

The local virtual environment:

```text
.venv/
```

should **not** be committed.

---

# 🚀 Installation

## Prerequisites

Make sure the following are installed:

* Python 3.12+
* `uv`
* Git
* Google Gemini API key

---

## 1. Clone the Repository

```bash
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPOSITORY>.git
```

Move into the project:

```bash
cd <YOUR_REPOSITORY>
```

---

# 2. Install Dependencies

Because this project uses `uv`, run:

```bash
uv sync
```

This will create the virtual environment and install the dependencies specified in:

```text
pyproject.toml
```

using the versions resolved in:

```text
uv.lock
```

---

# 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

Never commit the real `.env` file.

The repository should contain:

```text
.env.example
```

with:

```env
GOOGLE_API_KEY=
```

---

# ▶️ Running the Project

## Start the MCP Server

Run:

```bash
uv run python server.py
```

The MCP server will start and wait for client connections.

---

## Run the MCP Client

In another terminal:

```bash
uv run python client.py
```

The client will:

1. Connect to the MCP server.
2. Discover available tools.
3. Display the available tools.
4. Accept a user query.
5. Send the query and tool definitions to Gemini.
6. Allow Gemini to select a tool.
7. Execute the selected MCP tool.
8. Return the tool result to Gemini.
9. Generate the final response.

---

# 🧠 Tool Calling Flow

Consider this example:

```text
User:

Fetch the latest news for HDFC Bank.
```

Gemini analyzes the available tools.

If it finds:

```text
get_latest_news(company: str)
```

it can generate:

```text
Tool Call:

get_latest_news
company = "HDFC Bank"
```

The MCP client receives this request.

It then executes:

```text
MCP Client
    ↓
call_tool("get_latest_news", ...)
```

The MCP server executes:

```python
get_latest_news("HDFC Bank")
```

The result travels back:

```text
MCP Server
    ↓
MCP Client
    ↓
Gemini
```

Gemini then produces the final response.

---

# 🔁 Multiple Tool Calls

The architecture can also support multiple tool calls.

For example, suppose the user asks:

```text
Get the current stock price of HDFC Bank and
fetch the latest news about it.
```

Gemini may determine that two tools are required:

```text
get_stock_price("HDFC Bank")
get_latest_news("HDFC Bank")
```

The client can execute the required MCP tools and provide their results back to Gemini.

Conceptually:

```text
                    Gemini
                       │
              ┌────────┴────────┐
              │                 │
              ▼                 ▼
       get_stock_price    get_latest_news
              │                 │
              ▼                 ▼
         MCP Server         MCP Server
              │                 │
              └────────┬────────┘
                       ▼
                  Tool Results
                       │
                       ▼
                    Gemini
                       │
                       ▼
                 Final Answer
```

---

# 🎯 Key MCP Concepts Demonstrated

This project is designed to demonstrate the core MCP concepts.

## MCP Server

The server exposes capabilities to AI applications.

```text
MCP Server
    ↓
Tools
```

---

## MCP Client

The client connects an AI application to the MCP server.

```text
LLM Application
      ↓
MCP Client
      ↓
MCP Server
```

---

## Tools

Tools are executable functions exposed by the MCP server.

Example:

```python
@mcp.tool()
def calculate_sum(a: int, b: int) -> int:
    return a + b
```

---

## Tool Discovery

The client can discover the tools exposed by the MCP server.

This makes the architecture more dynamic than hard-coding every available function inside the client.

---

## Tool Selection

The LLM decides which tool is appropriate based on:

* User request
* Tool name
* Tool description
* Tool parameters

---

## Tool Execution

The actual execution happens outside the LLM.

This is an important architectural principle.

```text
LLM
 ↓
Decision
 ↓
Tool Call
 ↓
Application
 ↓
Tool Execution
```

The LLM does not directly execute Python code.

---

# 🔒 Security Considerations

Never expose API keys in source code.

Bad:

```python
api_key = "AIza..."
```

Good:

```python
import os

api_key = os.getenv("GOOGLE_API_KEY")
```

Use:

```text
.env
```

for local secrets and ensure it is included in `.gitignore`.

---

# 🧩 MCP vs Traditional Function Calling

Traditional function calling often looks like:

```text
Application
    │
    ├── Tool A
    ├── Tool B
    └── Tool C
```

The application itself owns the tools.

With MCP:

```text
                  MCP Client
                      │
             MCP Protocol
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
   MCP Server A  MCP Server B  MCP Server C
        │             │             │
      Tools         Tools         Tools
```

This provides a more standardized architecture for connecting AI applications with external capabilities.

---

# 🧠 MCP and RAG

MCP can also be used alongside Retrieval-Augmented Generation (RAG).

For example, an MCP server could expose:

```text
search_documents()
retrieve_chunks()
query_vector_database()
get_document_metadata()
```

The architecture could become:

```text
                     Gemini
                        │
                        ▼
                 MCP Client
                        │
                        ▼
                 MCP Server
                        │
             ┌──────────┼──────────┐
             ▼          ▼          ▼
          Pinecone    MongoDB     APIs
             │
             ▼
        Relevant Chunks
             │
             ▼
           Gemini
             │
             ▼
        Final Response
```

This means MCP can act as a standardized interface between an LLM application and components of a RAG system.

---

# 🔗 MCP with LangChain / LangGraph

MCP is not a replacement for frameworks such as LangChain or LangGraph.

They solve different problems.

### MCP

Focuses on:

```text
Standardized communication
between AI applications and tools/data
```

### LangChain

Provides abstractions for:

```text
LLMs
Prompts
Retrievers
Tools
Agents
Chains
Vector Stores
```

### LangGraph

Focuses on:

```text
Stateful
multi-step
agent workflows
```

They can therefore be used together.

A possible architecture is:

```text
                LangGraph
                    │
                    ▼
               LLM / Agent
                    │
                    ▼
                MCP Client
                    │
                    ▼
                MCP Server
                    │
          ┌─────────┼─────────┐
          ▼         ▼         ▼
       Vector DB   APIs    Databases
```

---

# 🧪 Example Use Cases

The MCP architecture demonstrated in this project can be extended to many real-world applications.

### Financial AI Assistant

Expose tools such as:

```text
get_stock_price()
get_financial_statements()
get_latest_news()
calculate_financial_ratio()
```

---

### RAG Application

Expose:

```text
search_documents()
retrieve_document()
search_vector_database()
```

---

### Enterprise AI Assistant

Expose:

```text
search_employee_data()
query_database()
search_internal_documents()
create_ticket()
```

---

### Developer Assistant

Expose:

```text
search_github()
get_issue()
create_issue()
search_repository()
```

---

# 📊 Project Learning Objectives

This project was created to understand:

* What MCP is
* Why MCP is required
* MCP client/server architecture
* MCP tool discovery
* MCP tool definitions
* Function declarations
* LLM tool selection
* Tool calling
* Tool execution
* Returning tool results to an LLM
* Multiple tool calls
* Gemini integration
* Async MCP communication
* `uv` project management
* MCP integration patterns for RAG
* MCP integration patterns for agentic applications

---

# 💡 Important Architectural Insight

The most important concept demonstrated by this project is the separation of responsibilities.

### Gemini

Responsible for:

```text
Understanding the user
        ↓
Deciding what capability is required
        ↓
Selecting the appropriate tool
```

### MCP Client

Responsible for:

```text
Connecting to MCP servers
        ↓
Discovering tools
        ↓
Sending tool definitions to Gemini
        ↓
Executing requested MCP tools
        ↓
Returning results to Gemini
```

### MCP Server

Responsible for:

```text
Exposing tools
        ↓
Executing tools
        ↓
Returning results
```

Therefore:

> **The LLM decides what should happen; the MCP server provides the capability to make it happen.**

---

# 🛠️ Future Improvements

Possible extensions for this project include:

* Add multiple MCP servers
* Add database tools
* Add web-search tools
* Add filesystem tools
* Add authentication
* Add logging
* Add error handling
* Add retry mechanisms
* Add structured tool responses
* Add Pydantic validation
* Add streaming responses
* Add parallel tool execution
* Add LangChain integration
* Add LangGraph agent orchestration
* Integrate MCP tools into a RAG pipeline
* Add automated tests
* Containerize the MCP server using Docker

---

# 📚 Project Architecture Summary

The complete architecture can be summarized as:

```text
┌──────────────────────────────┐
│            User              │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│          Gemini LLM          │
│                              │
│  Understands user request    │
│  Selects appropriate tool    │
└──────────────┬───────────────┘
               │
               │ Tool Call
               ▼
┌──────────────────────────────┐
│         MCP Client           │
│                              │
│  • Tool Discovery            │
│  • Function Declarations     │
│  • Tool Invocation           │
│  • Result Handling           │
└──────────────┬───────────────┘
               │
               │ MCP Protocol
               ▼
┌──────────────────────────────┐
│         MCP Server           │
│                              │
│       Exposed Tools          │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       External Systems       │
│                              │
│ APIs / Databases / Files /   │
│ RAG / Business Logic         │
└──────────────┬───────────────┘
               │
               │ Tool Result
               ▼
┌──────────────────────────────┐
│          Gemini LLM          │
│                              │
│     Generates final answer   │
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│            User              │
└──────────────────────────────┘
```

---

# 🆕 Latest Project Update — MySQL Database MCP Tool

The project has now been extended with MySQL database integration through MCP.

A dedicated database capability has been added so Gemini can interact with MySQL through MCP tools without embedding database logic directly into the LLM application.


Database MCP Tools

The MCP server now exposes two database tools:

get_database_schema()
execute_sql()

get_database_schema()

Retrieves the schema of one or more MySQL tables, including:

Table name

Column names

Data types

Primary keys

Nullability

This allows Gemini to understand the database structure before generating SQL.

execute_sql()

Executes a read-only SQL SELECT query against the MySQL database and returns the query results to Gemini.

Only SELECT queries are allowed.

---

Database Tool Calling Flow

For a database-related question, the flow is now:

User
  ↓
Gemini
  ↓
Determine database information is required
  ↓
get_database_schema()
  ↓
MCP Server
  ↓
MySQL
  ↓
Schema returned
  ↓
Gemini
  ↓
Generate SQL SELECT query
  ↓
execute_sql()
  ↓
MCP Server
  ↓
MySQL
  ↓
Query Result
  ↓
Gemini
  ↓
Final Answer

For example:

User:

Display the names of employees and the projects
assigned to them.

Gemini can first request the required table schemas:

get_database_schema(
    table_names=[
        "employees",
        "employee_projects",
        "projects"
    ]
)

After receiving the schema, Gemini generates the appropriate SQL query and invokes:

execute_sql()

The returned database records are then provided back to Gemini so it can generate the final natural-language response.

---

Separation of Responsibilities

The database integration follows a clear separation between the LLM, MCP client, MCP server, and database.

Gemini
   │
   │ Tool Selection
   ▼
MCP Client
   │
   │ MCP Tool Call
   ▼
MCP Server
   │
   ▼
Database Tool
   │
   ▼
MySQL Database

The database connection and schema logic are maintained separately from the MCP tool layer.

Gemini is responsible for:

Understanding the user's request
        ↓
Determining when database information is required
        ↓
Selecting the database tool
        ↓
Generating the SQL query
        ↓
Interpreting the query result

The MCP database layer is responsible for:

Connecting to MySQL
        ↓
Retrieving database schemas
        ↓
Executing SELECT queries
        ↓
Returning database results

Prompt Template Integration

The existing SQL prompt-template concept has also been adapted to the MCP architecture.

Instead of embedding Gemini directly inside the database implementation, the instructions are provided to Gemini through the system prompt.

The instructions guide Gemini to:

Identify when a database query is required.

Retrieve the database schema when necessary.

Use the returned schema to generate SQL.

Generate only SELECT queries.

Execute the query through the execute_sql MCP tool.

Use the returned data to generate the final answer.

This keeps LLM instructions and reasoning on the client side, while the MCP server remains responsible for providing and executing the database capability.



# ⭐ Conclusion

This project provides a practical implementation of the **Model Context Protocol (MCP)** and demonstrates how an LLM can interact with external tools through a standardized client-server architecture.

Rather than directly coupling Gemini with every application-specific function, MCP provides a reusable interface through which AI applications can discover and invoke capabilities.

The project demonstrates the complete lifecycle:

```text
Discover Tools
      ↓
Provide Tools to LLM
      ↓
LLM Selects Tool
      ↓
MCP Client Invokes Tool
      ↓
MCP Server Executes Tool
      ↓
Result Returned
      ↓
LLM Generates Final Answer
```

This architecture can serve as a foundation for building more advanced **Agentic AI, RAG, enterprise AI assistants, and tool-using LLM applications**.
