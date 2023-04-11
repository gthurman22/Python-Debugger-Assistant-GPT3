#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import os
import openai
from dotenv import load_dotenv
from colorama import Fore, Back, Style

#load values from the .env file if it exists
load_dotenv()

#configure OpenAI Model
with open('top_secret.txt') as file: # Added error handling in case file is not found
    try:   # Attempt to read the API key from the 'top_secret.txt' file.
           # If the file is not found, print an error message and continue.
            openai.api_key = file.read()
    except FileNotFoundError:
        print("API key file not found")

# Changed the AI assistant's instructions to include the topic of debugging
INSTRUCTIONS = """You are an AI assistant that is an expert in debugging python code. If you are unable to provide an answer to a debugging question, ask the end-user to re-submit the code. Your primary goal is to try and fix code errors, and provide solutions to the errors, assuming the end-user has basic python scripting knowledge.
"""

ANSWER_SEQUENCE = "\nAI:"

# Prompts the bot to respond
QUESTION_SEQUENCE = "\nHuman: "

# How the bot knows our questions
TEMPERATURE = 0.5
MAX_TOKENS = 500
FREQUENCY_PENALTY = 0
PRESENCE_PENALTY = 0.6

# limits how many questions we include in the prompt
MAX_CONTEXT_QUESTIONS = 10

# function to generate a solution to the debugging question
def get_solution(prompt):
    """
    Get a solution to a debugging question

    Parameters:
        prompt (str): The prompt to use to generate the solution

    Returns the solution to the debugging question
    """
    # insert code here to generate the debugging solution
    # using openai.Completion.create()

# How the bot recalls what we've been talking about during chat
def get_response(prompt):
    """
    Get a response from the model using the prompt

    Parameters:
        prompt (str): The prompt to use to generate the response

    Returns the response from the model
    """
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=1,
            frequency_penalty=FREQUENCY_PENALTY,
            presence_penalty=PRESENCE_PENALTY,
    )
        return response.choices[0].text
    
    # handle any OpenAI errors
    except openai.error.OpenAIError as error:
        print("OpenAI error:", error)
        return "I'm sorry, I'm having trouble generating a response. Please try again later."

# checks whether a question is safe to ask the model
def get_moderation(question):
    """
    Check that the question is safe to ask the model

    Parameters:
        question (str): The question to check

    Returns a list of errors if the question is not safe, otherwise returns None
    """
    errors = {
        "hate": "Content that expresses, incites, or promotes hate based on race, gender, ethnicity, religion, nationality, sexual orientation, disability status, or caste.",
        "hate/threatening": "Hateful content that also includes violence or serious harm towards the targeted group.",
        "self-harm": "Content that promotes, encourages, or depicts acts of self-harm, such as suicide, cutting, and eating disorders.",
        "sexual": "Content meant to arouse sexual excitement, such as the description of sexual activity, or that promotes sexual services (excluding sex education and wellness).",
        "sexual/minors": "Sexual content that includes an individual who is under 18 years old.",
        "violence": "Content that promotes or glorifies violence or celebrates the suffering or humiliation of others.",
        "violence/graphic": "Violent content that depicts death, violence, or serious physical injury in extreme graphic detail.",
    }

    # Added error handling for cases where the OpenAI Moderation API request fails
    try:
        response = openai.Moderation.create(input=question)
    except openai.error.OpenAIError:
        #Catch any openAI errors that may occur during API Request
        print("Moderation API request failed")
        return ["Moderation API request failed"]    

    if response.results[0].flagged:
        # get the categories that are flagged and generate a message
        result = [
            error
            for category, error in errors.items()
            if response.results[0].categories[category]
        ]
        return result
    return None


def main():
    os.system("cls" if os.name == "nt" else "clear")
    # keep track of previous questions and answers
    previous_questions_and_answers = []
    while True:
        # ask the user for their question
        new_question = input(
            Fore.GREEN + Style.BRIGHT + "What should we debug today?: " + Style.RESET_ALL
        )
        # check the question is safe
        errors = get_moderation(new_question)
        if errors:
            print(
                Fore.RED
                + Style.BRIGHT
                + "Sorry, a technical error has occured:"
            )
            for error in errors:
                print(error)
            print(Style.RESET_ALL)
            continue
        # build the previous questions and answers into the prompt
        # use the last MAX_CONTEXT_QUESTIONS questions
        context = ""
        for question, answer in previous_questions_and_answers[-MAX_CONTEXT_QUESTIONS:]:
            context += QUESTION_SEQUENCE + question + ANSWER_SEQUENCE + answer

        # add the new question to the end of the context
        context += QUESTION_SEQUENCE + new_question + ANSWER_SEQUENCE

        # get the response from the model using the instructions and the context
        response = get_response(INSTRUCTIONS + context)

        # add the new question and answer to the list of previous questions and answers
        previous_questions_and_answers.append((new_question, response))

        # print the response
        print(Fore.CYAN + Style.BRIGHT + "Here you go: " + Style.NORMAL + response)


if __name__ == "__main__":
    main()
           


# In[ ]:




