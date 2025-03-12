import json
from openai import OpenAI

class OpenAiSqlGenerator:
    def __init__(self, open_ai_key: str, schema: dict, default_prompt: str = """
    Given the database schema, write an SQL query to answer the query.
    Database Schema:
    {schema}

    Query: {query} Only dump the sql query like this {{"sql": "QUERY", "description": ""}}, nothing else, and describe as little as possible.
    
    SQL Query:
    """):
        self.client = OpenAI(api_key=open_ai_key)  
        self.schema = json.dumps(schema, indent=4)  
        self.default_prompt = default_prompt

    def generate_sql(self, query: str):
        prompt = self.default_prompt.format(schema=self.schema, query=query)

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Latest GPT model
                #model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are an SQL expert."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0  # Keep responses deterministic
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error generating SQL: {str(e)}"
