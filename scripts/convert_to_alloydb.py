import sqlite3
import re

def sqlite_to_postgres(sqlite_db_path, output_sql_path):
    conn = sqlite3.connect(sqlite_db_path)
    
    with open(output_sql_path, 'w', encoding='utf-8') as f:
        f.write("-- AlloyDB (PostgreSQL) Migration Script\n")
        f.write("-- Generated from cure_quest.db\n\n")
        f.write("BEGIN;\n\n")
        
        for statement in conn.iterdump():
            # Skip SQLite internal tables and specific metadata
            if 'sqlite_sequence' in statement or 'CREATE UNIQUE INDEX' in statement:
                continue
            
            # 1. Primary Key and Type conversion
            if 'CREATE TABLE' in statement:
                # Replace id column with SERIAL PRIMARY KEY (flexible regex for spaces/tabs/quotes)
                statement = re.sub(r'\b"?id"?\s+INTEGER\s+NOT\s+NULL', 'id SERIAL PRIMARY KEY', statement)
                
                # Remove trailing PRIMARY KEY (id) constraints (common in SQLite)
                statement = re.sub(r',\s*PRIMARY\s+KEY\s*\("?id"?\)', '', statement)
                
                # Convert common SQLite types to Postgres
                statement = statement.replace('DATETIME', 'TIMESTAMP WITH TIME ZONE')
                statement = statement.replace('BOOLEAN', 'BOOLEAN')
            
            # 2. Syntax cleanup
            statement = statement.replace('AUTOINCREMENT', '')
            
            # 3. Skip SQLite transaction commands
            if statement.strip() in ['COMMIT;', 'BEGIN TRANSACTION;', 'ROLLBACK;']:
                continue
                
            f.write(statement + '\n')
            
        f.write("\nCOMMIT;\n")
    
    conn.close()
    print(f"Migration script created: {output_sql_path}")

if __name__ == "__main__":
    sqlite_to_postgres(r'.\frontend\cure_quest.db', 'alloydb_init.sql')
