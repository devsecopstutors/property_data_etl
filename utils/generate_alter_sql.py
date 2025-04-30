# utils/generate_alter_sql.py

def generate_alter_table_sql(table_name, columns, schema="public"):
    """
    Generate ALTER TABLE statements to change column types to BIGINT.
    
    Args:
        table_name (str): Table to alter.
        columns (List[str]): List of column names to alter.
        schema (str): Schema name (default: public).
        
    Returns:
        List[str]: List of ALTER TABLE SQL statements.
    """
    sql_statements = []
    
    for col in columns:
        sql = f'ALTER TABLE "{schema}"."{table_name}" ALTER COLUMN "{col}" TYPE BIGINT;'
        sql_statements.append(sql)
        
    return sql_statements

