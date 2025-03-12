from pprint import pprint
import json
import re
from sqlalchemy import text
from src.datasource.db import Database, RDatasourceInspector
from src.plugins.open_ai import OpenAiSqlGenerator


def extract_json(text: str) -> dict:
    """Extract JSON object from a mixed text response."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))  # Convert to dictionary
        except json.JSONDecodeError:
            print("Error decoding JSON")
    return {}

async def bootstrap():

    open_ai_key = "sk-proj-"

    db = Database("sqlite:///sakila.sqlite")
    session = db.get_session()
    
    db_inspector = RDatasourceInspector(db)
    schema: dict = db_inspector.dump_schema()
    
    openai_client = OpenAiSqlGenerator(open_ai_key, schema)
    skip_model = False
    try:
        while True:
            query = input("Ask Model: ").strip()
            if query.lower() == "exit":
                break

            if query.lower() == "skip":
                skip_model = True

            ai_query = {"sql": None}
            if not skip_model:
                response = openai_client.generate_sql(query)
                print("response: ", response, type(response))
                ai_query = extract_json(response)

            selected_query = ai_query["sql"] if ai_query["sql"] else input("SQL: ")

            result = session.execute(text(selected_query))
            if result:
                print("\nColumn Names:", ", ".join(result.keys()))
                for row in result:
                    print(row)
    finally:
        print("closed")
