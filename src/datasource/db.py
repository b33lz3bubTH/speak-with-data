from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
import os

class Database:
    _instance = None
    
    def __new__(cls, db_url=None):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            if db_url is None:
                db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../olist.sqlite'))
                db_url = f"sqlite:///{db_path}"
            elif not db_url.startswith("sqlite:///"):
                db_url = f"sqlite:///{os.path.abspath(db_url)}"
            cls._instance.engine = create_engine(db_url, connect_args={"check_same_thread": False})
            cls._instance.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=cls._instance.engine)
        return cls._instance
    
    def get_session(self):
        return self.SessionLocal()


class RDatasourceInspector:
    def __init__(self, db: Database):
        self.engine = db.engine  # Get the Engine object

    def dump_schema(self, output_file=None):
        inspector = inspect(self.engine)
        schemas = {}

        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)

            schemas[table_name] = {
                "columns": {col["name"]: str(col["type"]) for col in columns},
                "foreign_keys": [
                    {
                        "column": fk["constrained_columns"][0],
                        "references": fk["referred_table"],
                        "referred_column": fk["referred_columns"][0] if fk["referred_columns"] else None,
                    }
                    for fk in foreign_keys
                ],
            }

        if output_file:
            with open(output_file, "w") as f:
                json.dump(schemas, f, indent=4)
            return f"Schema saved to {output_file}"
        
        return schemas  # Return schema as a dictionary
