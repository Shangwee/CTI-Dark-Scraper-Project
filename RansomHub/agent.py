"""
Author: Derrick
File: agent.py
Date: 02/03/2025
---------
Description:
"""


import google.generativeai as genai


def chat_with_gemini(api_key, prompt, chat_history=None):
    """
    Connects to Gemini, sends a prompt, and maintains chat context.

    Args:
        api_key: Your Gemini API key.
        prompt: The text prompt to send to Gemini.
        chat_history: A list of dicts representing the chat history.

    Returns:
        A tuple containing the text response from Gemini and the updated chat history, or (None, None) if an error occurs.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash') # Or 'gemini-pro' or 'gemini-ultra'

        if chat_history is None:
            chat_history = []  # Initialize if no history

        chat_history.append({"role": "user", "parts": [prompt]}) #Add user prompt to history

        response = model.generate_content(chat_history)

        if hasattr(response, "parts") and response.parts: #Check for valid response
            gemini_response = response.parts[0].text
            chat_history.append({"role": "model", "parts": [gemini_response]}) #Add model response to history
            return gemini_response, chat_history
        else:
            return None, chat_history # Return the history, even if the response was bad.
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, chat_history #Return the history, even with an error.


def get_classification(desc):
    api_key = "#####" # Insert gemini API key
    if api_key == "YOUR_API_KEY":
        print("Please replace 'YOUR_API_KEY' with your actual API key.")
    else:
        chat_history = [{"role": "user", "parts": '''
You are a sophisticated AI capable of performing two distinct classification tasks based on a provided description.

**Task 1: Stolen Data Classification**

Given a description of stolen data, you will categorize it into one or more of the following standard cybersecurity categories:

* Personal Identifiable Information (PII)
* Financial & Payment Data
* Authentication & Credential Data
* Medical & Health Records (PHI)
* Corporate & Business Data
* Government & Military Data
* Intellectual Property (IP) & Research Data
* Communication & Social Data
* System & Infrastructure Data
* Dark Web & Underground Economy Data

**Task 2: Industry Classification**

You will also classify the entity associated with the data description according to the Global Industry Classification Standard (GICS). You will determine the appropriate GICS Sector and GICS Industry Group.

**Input:**

A description that includes both a description of stolen data and information about the entity involved. This description will be presented as a single text block.

**Output:**

Your response must strictly adhere to the following format:

Categories: [Comma-separated list of applicable categories from Task 1]
GICS Sector: [One of the 11 official GICS sectors]
GICS Industry Group: [The specific industry group under the identified sector]


**Important:**

* Return ONLY the output in the specified format.
* Do not include any additional text, explanations, or code blocks.
* Assume the entity is a company or organization.
* If the entity is a government or tribal entity, classify the industry based on their primary output.
* If the provided documents describe legal actions, assume the industry relates to the primary focus of the legal actions.

**Example Input:**

"Usernames, hashed passwords, and financial records from an online retail company specializing in outdoor gear. The company, 'Adventure Co.', also had legal documents stolen, that discuss legal disputes over land rights."

**Example Output:**

Categories: Authentication & Credential Data, Financial & Payment Data, Corporate & Business Data, Legal & Regulatory Data
GICS Sector: Consumer Discretionary
GICS Industry Group: Specialty Retail
       '''}]  # Initialize chat history
        user_prompt = desc
        if user_prompt:
            gemini_response, chat_history = chat_with_gemini(api_key, user_prompt, chat_history)

            if gemini_response:
                return gemini_response
            else:
                return "Gemini: There was a problem generating a response."


if __name__ == "__main__":
    pass