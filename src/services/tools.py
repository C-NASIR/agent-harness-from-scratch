import json

from openai.types.responses import FunctionToolParam

from src.services.internal_tools import search_history, search_knowledge_base
from src.services.orders import get_order

TOOLS: list[FunctionToolParam] = [
    {
        "type": "function", 
        "name": "get_order", 
        "description": "returns order status and arrival date", 
        "parameters": {
            "type": "object", 
            "properties": {
                "order_id": {"type": "string"}
            }, 
            "required": ['order_id'], 
            "additionalProperties": False
        }, 
        "strict": True
    }, 
    {
        "type": "function", 
        "name": "search_history", 
        "description": (
            "Search earlier messages and tool results"
            "in the customer's current conversation."
        ), 
        "parameters": {
            "type": "object", 
            "properties": {
                "query": {"type": "string"}
            }, 
            "required": ['query'], 
            "additionalProperties": False
        }, 
        "strict": True
    }, 
    {
        "type": "function", 
        "name": "search_knowledge_base", 
        "description": (
            "Search official store policies and products"
            "documentation to answer customer questions."
        ), 
        "parameters": {
            "type": "object", 
            "properties": {
                "query": {"type": "string"}
            }, 
            "required": ['query'], 
            "additionalProperties": False
        }, 
        "strict": True
    }
]

def is_this_a_tool(tool_name):
    return tool_name in {tool['name'] for tool in TOOLS}

def execute_tools(calls, conversation_id):
    results = []
    for call in calls:
        arguments = json.loads(call.arguments)

        if not is_this_a_tool(call.name):
            raise ValueError("we don't have that tool")

        print(f'we are using --> { call.name} tool')
        if call.name == 'get_order':
            response = get_order(arguments['order_id'])
        if call.name == 'search_history':
            response = search_history(arguments['query'], conversation_id)
        if call.name == "search_knowledge_base":
            response = search_knowledge_base(arguments['query'])

        results.append({
            "type": "function_call_output",
            "call_id": call.call_id, 
            "output": json.dumps(response)
        })
          
    return results