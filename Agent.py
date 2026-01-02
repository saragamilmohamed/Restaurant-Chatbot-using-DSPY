import dspy
import dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import dspy
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
# Setup
dotenv.load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


#GROQ_API_KEY = os.getenv("GROQ_API_KEY")

lm = dspy.LM(
    model="gemini/gemini-2.5-flash",
    api_key=GEMINI_API_KEY, temperature=0.8
)
dspy.configure(lm=lm)

# MCP Server connection
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server_res.py"],
    env=None,
)




class OrderDetails(BaseModel):
    """A structured object containing all details of the customer's order."""
    
    items: List[str] = Field(
        default_factory=list,
        description="A list of food or drink items the customer wants to order."
    )
    special_requests: List[str] = Field(
        default_factory=list,
        description="Any special requests or modifications for the items (e.g., 'no onions', 'extra cheese')."
    )
    name: Optional[str] = Field(
        default=None,
        description="The customer's name for the order."
    )
    table_or_location: Optional[str] = Field(
        default=None,
        description="The customer's table number or delivery location (e.g., 'Table 7')."
    )
    phone: Optional[str] = Field(
        default=None,
        description="The customer's contact phone number."
    )

class AgentTurn(BaseModel):
    """
    The complete output for a single turn of the conversation, including the
    text response, internal state, updated order, and any tool calls.
    """
    
    response: str = Field(
        description="The warm, polite, and conversational text response to be shown to the customer."
    )
    state: Literal[
        'GREET', 'VIEW_MENU', 'PLACE_ORDER', 'MODIFY_ORDER', 
        'PROVIDE_INFO', 'CONFIRM_ORDER', 'CANCEL', 'FINALIZED'
    ] = Field(
        description="The agent's internal state after processing the message."
    )
    order: OrderDetails = Field(
        description="The updated and structured details of the customer's order."
    )
    tools_called: List[str] = Field(
        default_factory=list,
        description="A list of tool functions to be called (e.g., 'get_menu', 'create_order', 'send_to_kitchen')."
    )
    confirmation_needed: bool = Field(
        default=False,
        description="A boolean flag indicating if the agent needs to ask the customer for confirmation."
    )


class RestaurantAgent(dspy.Signature):
    """
    You are a friendly restaurant waiter chatbot. Your task is to process a customer's message
    within the context of a chat history. You must greet customers, show the menu (via 'get_menu'),
    take orders (via 'create_order'), collect info (name, location, phone), and send the
    final order to the kitchen (via 'send_to_kitchen'). You must detect intent, extract entities,
    and respond warmly, repeating orders before confirmation and asking for missing details.
    """

    customer_message: str = dspy.InputField(
        desc="The most recent natural-language message from the customer."
    )
    chat_history: str = dspy.InputField(
        desc="The prior conversation history between the chatbot and the customer for context."
    )
    
    agent_turn: AgentTurn = dspy.OutputField(
        desc="The complete, structured output for this conversational turn, including the text response, state, order data, and tool calls."
    )



async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await session.list_tools()
            dspy_tools = [dspy.Tool.from_mcp_tool(session, tool) for tool in tools.tools]

            if not dspy_tools:
                print("Warning: No MCP tools found.")

            print("Restaurant Chatbot")
            print("=" * 50)
            print("Type 'quit' to exit\n")

            agent = dspy.ReAct(RestaurantAgent, tools=dspy_tools)
            history = []

            while True:
                user_input = input("You: ").strip()

                if "quit" in user_input.lower():
                    print("Thanks for visiting!")
                    break

                if not user_input:
                    continue

                history.append(f"Customer: {user_input}")

                try:
                    result = await agent.acall(
                        customer_message=user_input,
                        chat_history="\n".join(history[-10:])
                    )
                    response = result.agent_turn
                    history.append(f"Agent: {response.response}")
                    print(f"Agent: {response.response}\n")

                except Exception as e:
                    print(f"Error: {e}\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())