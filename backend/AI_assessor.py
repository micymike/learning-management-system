""" this file is responsible for assessing the AI generated code. so based on the given rubric, it will assess the code and return the score the data will be used to generate a report and also we will get the name of the student and the girhub url from csv.py and the analyzed codes from repo_analyzer.py we will use gpt3.5-turbo"""

import os
import json
import requests
import pandas as pd
from repo_analyzer import analyze_repo
# Removed unused import of read_csv from csv_analyzer
from rubric_handler import load_rubric
import openai
import dotenv

dotenv.load_dotenv()

try:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception as e:
    print(f"Error: {e} check your environment for openai key")
    exit(1)

def assess_code(code, rubric, client):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a code quality assessor.check the following code for plagarism and if the code is AI generated. return the score based on the rubric. Always be honest and assertive"
                },
                {
                    "role": "user",
                    "content": f"Rubric: {rubric}\n\nCode: {code}"
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    csv_data = read_csv()
    rubric = load_rubric()
    scores = []
    for row in csv_data.itertuples():
        analyzed_code = analyze_repo(row.github_url)
        score = assess_code(analyzed_code, rubric, client)
        scores.append({
            "name": row.name,
            "github_url": row.github_url,
            "score": score
        })
    df = pd.DataFrame(scores)
    df.to_csv("scores.csv", index=False)
