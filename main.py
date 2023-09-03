import os
from typing import List
import spacy
import pandas as pd
import requests
from textbase import bot, Message
from textbase.models import OpenAI
import re
import PyPDF2
import io
# Configure the OpenAI API key from an environment variable
OpenAI.api_key = "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"

# Load a pre-trained spaCy model for NLP tasks
nlp = spacy.load("en_core_web_sm")

programming_languages_and_technologies = [
    "python", "java", "javascript", "html", "css", "sql", "c++",
    "php", "ruby", "swift", "typescript", "react", "angular", "node.js",
    "docker", "kubernetes", "git", "aws", "azure", "cloud", "linux",
    "android", "ios", "c#", ".net", "scala", "kotlin", "ruby on rails",
    "restful", "graphql", "mongodb", "postgresql", "mysql", "oracle",
    "nosql", "api", "json", "xml", "redux", "vue.js", "ember.js",
    "bootstrap", "jquery", "agile", "scrum", "kanban", "jira", "confluence",
    "continuous integration", "unit testing", "test automation", "devops",
    "microservices", "containers", "virtualization", "shell scripting",
    "bash", "powershell", "object-oriented programming", "functional programming",
    "machine learning", "artificial intelligence", "data analysis", "data science",
    "big data", "blockchain", "cybersecurity", "networking", "web development",
    "game development", "cloud computing", "serverless", "internet of things",
    "robotics", "automation", "software development", "full stack development",
    "front-end development", "back-end development", "database management",
    "data modeling", "system administration", "network administration",
    "technical support", "customer support", "project management",
    "software architecture", "user experience (UX)", "user interface (UI) design",
    "wireframing", "prototyping", "agile methodologies", "problem-solving",
    "communication skills", "teamwork", "leadership", "creativity", "adaptability",
    "critical thinking", "time management", "presentation skills", "technical writing"
]

def fetch_pdf_from_url(pdf_url):
    try:
        response = requests.get(pdf_url) # Requests to fetch the PDF URL
        response.raise_for_status()  # Check for any HTTP request errors
        
        pdf_content = response.content
        return pdf_content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching PDF from URL: {e}")
        return None

def extract_text_from_pdf(pdf_content):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
    text = ''
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text



# Dictionary to store user information
user_info = {
    "intent": None,
    "job_role": None,
    "graduation": None,
    "graduation_year": None,
    "skill_set": None,
    "preferred_location": None,
    "pdfurl":None,
}


def is_job_related(text):
    # You can use spaCy or other NLP libraries to analyze the user's input
    doc = nlp(text.lower())
    
    # Define job-related keywords or phrases
    job_keywords = ["job","manual", "career", "employment", "work", "position", "Openings", "Jobseeker"]
    
    # Check if any of the job keywords is present in the user's input
    for keyword in job_keywords:
        if keyword in text.lower():
            return True
    
    return False

def is_job_relatedresume(text):
    # You can use spaCy or other NLP libraries to analyze the user's input
    doc = nlp(text.lower())
    
    # Define job-related keywords or phrases
    job_keywords = ["resume","pdf", "cv", "automatic", "suggest"]
    
    # Check if any of the job keywords is present in the user's input
    for keyword in job_keywords:
        if keyword in text.lower():
            return True
    
    return False



def get_job_listings(
    job_roles, graduation, graduation_year, skill_set, preferred_location
):
    # Read job listings from the .csv file into a DataFrame
    job_listings_df = pd.read_csv("joblist.csv")
    job_listings_df.dropna(subset=["Qualifications"], inplace=True)

    # Split the input strings into lists (assuming they are comma-separated)
    job_roles = job_roles.split(",")
    skill_set = skill_set.split(",")
    preferred_location = preferred_location.split(",")
    print(skill_set)
    # Create regex patterns for job roles, skill sets, and locations
    job_pattern = "|".join(re.escape(job) for job in job_roles)
    skill_pattern = "|".join(re.escape(skill) for skill in skill_set)
    location_pattern = "|".join(re.escape(location) for location in preferred_location)

    # Filter job listings based on user input
    filtered_jobs = job_listings_df[
        (job_listings_df["JobRole"].str.contains(job_pattern, case=False, regex=True))
        & (job_listings_df["Graduation"].str.contains(graduation, case=False))
        & (job_listings_df["Batch"].astype(str).str.contains(graduation_year, case=False))
        & (job_listings_df["Qualifications"].str.contains(skill_pattern, case=False, regex=True))
        & (job_listings_df["Location"].str.contains(location_pattern, case=False, regex=True))
    ]

    # Convert filtered job listings to a list of dictionaries
    job_listings = filtered_jobs.to_dict(orient="records")

    return job_listings


user_intent=" "
jobfillstatus="False"
bot_response=""

@bot()
def on_message(message_history: List[Message], state: dict = None):
	
    # Extract user input from the latest message
    user_input = message_history[-1].get("content", "") if message_history else ""
    print("user input =", user_input)

    # Determine user intent based on user_input
    global bot_response, user_intent, jobfillstatus
    user_intent = user_input[0]["value"]
    
    if is_job_relatedresume(user_intent):
    	bot_response = "please enter the pdf url"
    	user_info["pdfurl"] = "pdf"

    elif user_info["pdfurl"] == "pdf":
    	user_info["pdfurl"] = user_input[0]["value"]
    	pdf_content=fetch_pdf_from_url(user_info["pdfurl"])
    	if pdf_content:
		    # Extract text from the PDF resume
		    resume_text = extract_text_from_pdf(pdf_content)

		    # Display the entire extracted resume text
		    print("Extracted Resume:")
		    print(resume_text)

		    # Load the job dataset
		    job_dataset = pd.read_csv("joblist.csv")

		    # Find words that match the predefined list
		    matched_words = []
		    for word in programming_languages_and_technologies:
		        if re.search(rf'\b{re.escape(word)}\b', resume_text, re.IGNORECASE):
		            matched_words.append(word)

		    # Display the matched words
		    if matched_words:
		        print("\nMatched Words:")
		        print(matched_words)
		    else:
		        print("\nNo matching words found in the resume.")

		    # Search for jobs that match the matched words
		    def find_matching_jobs(matched_words):
		        matching_jobs = []

		        for index, row in job_dataset.iterrows():
		            job_skills = str(row['Qualifications']).lower().split(',')

		            # Check if any of the job skills match the matched words
		            for skill in job_skills:
		                if skill.strip().lower() in matched_words:
		                    matching_jobs.append(row)

		        return matching_jobs

		    # Find jobs that match the matched words
		    matching_jobs = find_matching_jobs(matched_words)

		    if matching_jobs:
		        bot_response = "\nMatching Jobs:\n\n"
		        for idx, job in enumerate(matching_jobs, start=1):
		            bot_response += f"\nJob Title: {job['JobRole']}\n"
		            bot_response += f"\nSkill Set: {job['Qualifications']}\n"
		            bot_response += f"\nLocation: {job['Location']}\n"
		            bot_response += f"\nJob Experience Required: {job['Job Experience Required']}\n"
		            bot_response += f"\nExpected Salary: {job['Job Salary']}\n"
		            bot_response += f"\nApply Link: {job['Link']}\n\n"
		            bot_response += f"\n--------------------------\n"
		    else:
		        bot_response="\nNo matching jobs found."
    # Based on the user intent, generate an appropriate response
    elif jobfillstatus=="True" and user_info["intent"] == "1":
    	user_info["job_role"] = user_input[0]["value"]
    	Display()

    elif jobfillstatus=="True" and user_info["intent"] == "2":
    	user_info["skill_set"] = user_input[0]["value"]
    	Display()

    elif jobfillstatus=="True" and user_info["intent"] == "3":
    	user_info["preferred_location"] = user_input[0]["value"]
    	Display()

    elif jobfillstatus=="True" and user_info["intent"] == "exit":
    	jobfillstatus=0
    	user_info["intent"] = "none"

    elif jobfillstatus=="True":
    	if user_intent == "exit":
            bot_response = "\n\nThank You for visiting Us!\n"
            jobfillstatus="False"
            user_info["intent"] = "none"
    	if user_intent == "3":
            bot_response = "\n\nEnter the new Location\n"
            user_info["intent"] = "3"

    	if user_intent == "2":
            bot_response = "\n\nEnter the new Skill Set\n"
            user_info["intent"] = "2"

    	if user_intent == "1":
            bot_response = "\n\nEnter the new Job Title\n"
            user_info["intent"] = "1"
        

    elif is_job_related(user_intent):
        # Ask for job role
        bot_response = "Great! Let's start your job search. Please specify your desired job role."
        user_info["intent"] = "job_search"

    elif user_info["intent"] == "job_search":
        # Store the user's input for job role
        user_info["job_role"] = user_input[0]["value"]

        # Ask for graduation
        bot_response = "Got it! Please specify your highest level of graduation (e.g., Btech, MS, phd)."
        user_info["intent"] = "graduation"

    elif user_info["intent"] == "graduation":
        # Store the user's input for graduation
        user_info["graduation"] = user_input[0]["value"]

        # Ask for graduation year
        bot_response = "Thanks! Please specify your graduation year (e.g., 2022, 2023)."
        user_info["intent"] = "graduation_year"

    elif user_info["intent"] == "graduation_year":
        # Store the user's input for graduation year
        user_info["graduation_year"] = user_input[0]["value"]

        # Ask for skill set
        bot_response = "Excellent! Please specify your skill set or key qualifications."
        user_info["intent"] = "skill_set"

    elif user_info["intent"] == "skill_set":
        # Store the user's input for skill set
        user_info["skill_set"] = user_input[0]["value"]

        # Ask for preferred location
        bot_response = "Great! Finally, please specify your preferred job location."
        user_info["intent"] = "preferred_location"

    elif user_info["intent"] == "preferred_location":
        # Store the user's input for preferred location
        user_info["preferred_location"] = user_input[0]["value"]
        Display()
    else:
        # If the intent is not recognized, provide a default response
        bot_response = "Hello, I am Your Job Provider\n\n"
        bot_response+="\nIf you want to get jobs based on your resume then please enter \"resume\"\n\n"
        bot_response+="\nIf you want to get jobs based on your manual input then please enter \"manual\""


    # Format the response in the required structure
    response = {
        "data": {
            "messages": [
                {
                    "data_type": "STRING",
                    "value": bot_response
                }
            ],
            "state": state
        },
        "errors": [
            {
                "message": ""
            }
        ]
    }

    return {
        "status_code": 200,
        "response": response
    }

def Display():
    global jobfillstatus, bot_response, user_intent  # Use global to modify the variable defined outside the function
    jobfillstatus = "True"

    job_listings = get_job_listings(
        user_info["job_role"],
        user_info["graduation"],
        user_info["graduation_year"],
        user_info["skill_set"],
        user_info["preferred_location"],
    )
    if job_listings:
        # Include job listings in the response
        bot_response = "\n\nHere are some job listings based on your preferences:\n"
        for job in job_listings:
            bot_response += f"\nJob Title: {job['JobRole']}\n"
            bot_response += f"\nSkill Set: {job['Qualifications']}\n"
            bot_response += f"\nExpected Salary: {job['Job Salary']}\n"
            bot_response += f"\nApply Link: {job['Link']}\n"
            bot_response += f"\nLocation: {job['Location']}\n"
            bot_response += f"\n--------------------------\n"
        bot_response += "\n\nIf you want to change the Job Title then Enter the 1.\n"
        bot_response += "\n\nIf you want to change the Skill set then Enter the 2.\n"
        bot_response += "\n\nIf you want to change the Job Location then Enter the 3.\n"
        bot_response += "\n\nIf you want to exit then enter exit.\n"
        user_info["intent"] = "none"
    else:
        bot_response = "\n\nI couldn't find any job listings based on your preferences."
        bot_response += "\n\nIf you want to change the Job Title then Enter the 1.\n"
        bot_response += "\n\nIf you want to change the Skill set then Enter the 2.\n"
        bot_response += "\n\nIf you want to change the Job Location then Enter the 3.\n"
        bot_response += "\n\nIf you want to exit then enter exit.\n"
        user_info["intent"] = "none"

   
if __name__ == "__main__":
    bot.run()

