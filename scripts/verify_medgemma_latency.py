import os
import time
import requests
from dotenv import load_dotenv

def measure_latency():
    # Load environment variables from .env
    load_dotenv()
    
    # Read the token from the .env file (it's stored as HUGGINGFACE_HUB_TOKEN)
    hf_token = os.getenv("HUGGINGFACE_HUB_TOKEN")
    
    if not hf_token:
        print("Error: HUGGINGFACE_HUB_TOKEN not found in .env file.")
        return

    # API configuration as requested (Fixed model ID to match .env and correct HF path)
    API_URL = "https://api-inference.huggingface.co/models/google/medgemma-1.5-4b-it"
    headers = {"Authorization": f"Bearer {hf_token}"}

    # Sample medical input payload
    payload = {
        "inputs": "What are the common side effects of metformin?",
        "parameters": {
            "max_new_tokens": 50,
            "temperature": 0.1
        }
    }

    print(f"Sending request to {API_URL}...")
    
    # Record the start time
    start_time = time.time()
    
    try:
        # Make the request
        response = requests.post(API_URL, headers=headers, json=payload)
        
        # Record the end time immediately after receiving the response
        end_time = time.time()
        
        # If the model is currently loading, HF might return a 503 with an estimated time
        response.raise_for_status()
        
        latency = end_time - start_time
        result = response.json()
        
        print("\n--- Results ---")
        print(f"Status Code: {response.status_code}")
        print(f"Latency: {latency:.4f} seconds")
        print("\nOutput Text:")
        
        # HF Inference API typically returns a list of dictionaries
        if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
            print(result[0]['generated_text'])
        else:
            print(result)
            
    except requests.exceptions.RequestException as e:
        print(f"\nRequest failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response body: {e.response.text}")
            
if __name__ == "__main__":
    print("Testing Hugging Face Inference API Latency...\n")
    measure_latency()
