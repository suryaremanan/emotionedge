import os
import requests
import os
import requests
import json
import logging

# Ensure these environment variables are set in your Docker or local environment
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://ollama:11434/api/generate")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "your_ollama_api_key")

def generate_recommendations(student_name, emotions):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OLLAMA_API_KEY}"
    }

    prompt = f"Student {student_name} has exhibited the following recorded emotions during class: {emotions}. Based on this data, please provide detailed recommendations for the student and the teacher to improve classroom engagement and learning outcomes. For example, if the student appears neutral, suggest ways to increase their participation and interest in the subject matter. If the student appears bored, recommend strategies to make the lessons more engaging and stimulating. If the student is attentive, suggest methods to maintain and further enhance their focus and attentiveness. Additionally, provide personalized tips for the student to maximize their learning potential and for the teacher to better address the student's needs."
    
    data = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx and 5xx)

        response_text = response.text
        data = json.loads(response_text)
        actual_response = data.get("response", "No recommendations available.")
        return actual_response

    except requests.exceptions.RequestException as e:
        logging.error(f"Request to Ollama API failed: {e}")
        if response.content:
            logging.error(f"Response content: {response.content}")
        return f"Error: {e}"

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return f"Error: {e}"
