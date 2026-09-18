###########################################################
# investigate.py
###########################################################

import json
import ollama

## Import the necessary functions from the parse_data module
from parse_data import load_items, get_unclaimed_items, save_result

## Build your prompt based on the description the user provides 
## and the items that are available in the lost-and-found database.
def build_prompt(description, available_items):
    system_prompt = """You are a strictly constrained data-matching assistant.
Rules for the Model:
- The model must use only the given JSON file data below to find matches.
- Not all the details of an item must match to be a possible match.
- Only JSON must be returned, with exactly the following structure:
{
    "matches": ["ITEM_ID"],
    "confidence": "LOW"
}
- "matches" contains all the possible matches (use the item's "id").
- "confidence" measures how confident the model is about the matches. 
- It must be exactly one of: LOW, MEDIUM, HIGH.
- If there is no match the model must return an empty list for matches."""

    items_string = json.dumps(available_items)
    
    user_prompt = f"User's lost item description: {description}\n\nAvailable Items Data:\n{items_string}"
    
    return system_prompt, user_prompt


## Logic to ask Qwen for all the possible matches based on the system prompt and user prompt.
def ask_qwen(system_prompt, user_prompt):
    # Using the local Ollama API to run the Qwen model. 
    response = ollama.chat(model='qwen3:8b', messages=[
        {
            'role': 'system',
            'content': system_prompt
        },
        {
            'role': 'user',
            'content': user_prompt
        }
    ])
    
    return response['message']['content']


## Logic to parse the response from Qwen and return the result. 
def parse_response(response_text):
    clean_text = response_text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    elif clean_text.startswith("```"):
        clean_text = clean_text[3:]
        
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
        
    clean_text = clean_text.strip()
    
    # Convert string to python dictionary
    result = json.loads(clean_text)
    return result


## Logic to validate the result returned by Qwen.
def validate_result(result, available_items):
    # 1. Check if the result is a dictionary
    if type(result) is not dict:
        return False
        
    # 2. Check if the required keys exist
    if "matches" not in result or "confidence" not in result:
        return False
        
    # 3. Check the values' types
    if type(result["matches"]) is not list or type(result["confidence"]) is not str:
        return False
        
    # 4. Validate confidence value
    if result["confidence"] not in ["LOW", "MEDIUM", "HIGH"]:
        return False
        
    # 5. Check if the item IDs are valid
    valid_ids = []
    for item in available_items:
        valid_ids.append(item["id"])
        
    for match_id in result["matches"]:
        if match_id not in valid_ids:
            return False
            
    return True


## Logic to display the matches found by Qwen in a user-friendly format.
def display_matches(result, available_items):
    print("\nMATCH RESULT")
    print("-" * 50)
    print(f"Confidence: {result['confidence']}\n")
    
    matches = result["matches"]
    
    if len(matches) == 0:
        print("No matches found.")
        print("[]\n")
    else:
        print("Possible matches:\n")
        
        for match_id in matches:
            # Find and print the matching item details
            for item in available_items:
                if item["id"] == match_id:
                    print(f"ID: {item['id']}")
                    print(f"Item: {item['item']}")
                    print(f"Color: {item['color']}")
                    print(f"Location: {item['location']}")
                    print(f"Date found: {item['date']}")
                    print()
                    break


## Control center for the entire program.
def main():

    data_filename = "found_items.json"
    
    print("CAMPUS LOST-AND-FOUND ASSISTANT")
    print("=" * 50)
    print()
    
    description = input("Describe the item you lost: ").strip()
    
    print("\nSearching for possible matches...")
    
    # Load and process data
    try:
        all_items = load_items(data_filename)
    except FileNotFoundError:
        print(f"Error: Database file '{data_filename}' not found.")
        return
        
    available_items = get_unclaimed_items(all_items)
    
    # AI logic
    system_prompt, user_prompt = build_prompt(description, available_items)
    
    try:
        response_text = ask_qwen(system_prompt, user_prompt)
        result = parse_response(response_text)
    except Exception as e:
        print(f"\nError communicating with Ollama or parsing response: {e}")
        return
        
    # Validate result
    is_valid = validate_result(result, available_items)
    
    if not is_valid:
        print("\nError: The AI returned an invalid data format.")
        print("Raw response from AI:", response_text)
        return
        
    # Display and Save
    display_matches(result, available_items)
    
    output_filename = "output/match_result.json"
    save_result(result, output_filename)
    print(f"Result saved to {output_filename}")


if __name__ == "__main__":
    main()

"""
AI Usage Declaration:
In accordance with the course guidelines, 
I used a free, open-source AI (local LLM) purely as a supplementary tool for non-core development tasks. 
Specifically, the AI assisted with identifying minor syntax errors, 
formatting the code to maintain a consistent personal style, and generating code comments to improve readability. 
The core algorithmic logic, step-by-step implementation, and data structure selection were developed entirely independently. 
I strictly complied with the course rules and confirm that no AI agent frameworks (such as OpenClaw, Dify, or MetaGPT) or paid models were used in the development of this assignment.
"""