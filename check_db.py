from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
load_dotenv()
url = os.environ.get('DATABASE_URL')
engine = create_engine(url)
with engine.connect() as conn:
  result = conn.execute(text('SELECT version()'))
  print(list(result))
