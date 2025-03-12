from pprint import pprint
from sqlalchemy import text
from src.datasource.db import Database, RDatasourceInspector
from src.plugins.open_ai import OpenAiSqlGenerator

async def bootstrap():

    open_ai_key = "sk-a2bj"

    db = Database("sqlite:///sakila.sqlite")
    session = db.get_session()
    
    db_inspector = RDatasourceInspector(db)
    schema: dict = db_inspector.dump_schema()
    
    openai_client = OpenAiSqlGenerator(open_ai_key, schema)
    skip_model = True
    while True:
        query = str(input("Ask Model: "))
        if query == "skip":
            skip_model = True
        
        if not skip_model:
            model_response = openai_client.generate_sql(query)
            print(model_response)
            
        selected_query = str(input("Sql: "))
        try:
            # Wrap the raw SQL query in the `text()` function
            result = session.execute(text(selected_query))

            # Print column names
            print("\nColumn Names:", ", ".join(result.keys()))

            # Print rows
            print("\nResults:")
            for row in result:
                print(row)
        except Exception as e:
            print(f"An error occurred: {e}")
        skip_model = False


