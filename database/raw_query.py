def make_query_insert_data(data: dict, table_name: str) -> str:
    return  f'''
    INSERT INTO {table_name} ({', '.join(data.keys())})
    VALUES {tuple(data.values())}
    '''


def make_query_get_rows(param: str, purpose_mean: str, table_name: str) -> str:
    return f'''
    SELECT *
    FROM {table_name}
    WHERE {param} = '{purpose_mean}'
    '''