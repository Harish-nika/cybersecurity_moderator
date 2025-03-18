from langchain_community.llms import Ollama
import json

# Load your custom Ollama model
llm = Ollama(model="cybersecurity-contentmoderator-wizardlm7bV4")  # Ensure the model name matches

def moderate_content(text: str):
    prompt = f"""
    Analyze the following text and classify it into predefined categories.
    Respond **ONLY in JSON format** without any extra text.

    Text: {text}
    """

    # Get response from Ollama
    response = llm.invoke(prompt).strip()

    # Validate JSON output
    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        print(f"⚠️ Model returned invalid JSON:\n{response}")
        return {"error": "Model response is not valid JSON", "raw_output": response}

    return result












""" model list
cybersecurity-contentmoderator-wizardlm7bV3:latest    707b72a6c67a    4.1 GB    4 days ago    
cybersecurity-contentmoderator-wizardlm7bV2:latest    6b76c19c4f0a    4.1 GB    4 days ago    
cybersecurity-contentmoderator-llama3.2b:latest       6864b06f99c5    2.0 GB    4 days ago    
cybersecurity-contentmoderator-deepseekR17b:latest    f969b11a2c6d    4.7 GB    4 days ago    
cybersecurity-contentmoderator-llama7b:latest         3da1c8a13ed6    4.9 GB    4 days ago    
llama3.1:latest                                       3c7b1eb10bef    4.9 GB    4 days ago    
deepseek-r1:latest                                    0a8c26691023    4.7 GB    4 days ago    
cybersecurity-moderator-wizardlm7b:latest             c1608c66ea63    4.1 GB    4 days ago    
llama3.2:latest                                       a80c4f17acd5    2.0 GB    4 days ago    
deepseek-r1:7b                                        0a8c26691023    4.7 GB    4 days ago    
cybersecurity-moderator-deepseek14b:latest            d8d0687cbe89    9.0 GB    4 days ago    
deepseek-r1:14b                                       ea35dfe18182    9.0 GB    4 days ago    
wizardlm2:7b                                          c9b1aff820f2    4.1 GB    4 days ago 
"""
