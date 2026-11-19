import json
import re

from src.services.conversations import load_conversation


def search_history(query, conversation_id):
    history, _ = load_conversation(conversation_id)

    terms = {
        word 
        for word in re.findall(r"\w+", query.lower())
        if len(word) >= 3
    }

    if not terms: return {"matches": []}

    matches = []

    for index, event in enumerate(history):
        text = event_text(event)

        words = set(re.findall(r"\w+", text))

        score = sum(
            1
            for term in terms
            if term in words
        )

        if score > 0:
            matches.append({
                "index": index, 
                "score": score, 
                "text": text[:1000]
            })
    
    matches.sort(key= lambda item: (-item['score'], -item['index']))

    return {"matches": matches[:5]}



def event_text(event):
    if event.get("type") == "function_call_output":
        output = event.get("output", "")
        if isinstance(output, str): return output
        return json.dumps(output)
    
    content = event.get("content", "")

    if isinstance(content, str): return content

    if isinstance(content, list):
        result = []
        for item in content:
            if isinstance(item, str): result.append(item)
            elif isinstance(item, dict): result.append(item.get("text", ""))
            else: result.append(json.dumps(item))
        
        return " ".join(result)
    
    return ""