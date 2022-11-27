import mysql.connector



db_user = "root"
db_password = "password"
db_host = "localhost"
db_name = "databaseproject"

def connect_to_database():
    connection = mysql.connector.connect(user=db_user, password=db_password,
                                         host=db_host, database=db_name)
    cursor = connection.cursor()
    return connection, cursor

# For stored procedures that return an array of rows containing multiple values
def unpack_results(stored_results):
    results = []
    col_names = []
    for result in stored_results:
        # Get the column names from the first data entry
        if len(col_names) == 0:
            for desc in result.description:
                col_names.append(desc[0])
        for row in result.fetchall():
            formatted_row = {}
            for i in range(len(col_names)):
                formatted_row.update({col_names[i]: row[i]})
            results.append(formatted_row)
    return results


# For stored procedures that only ever return one row
def unpack_single_result(stored_results):
    formatted_result = {}
    col_names = []
    for result in stored_results:
        # Pull column names
        for desc in result.description:
            col_names.append(desc[0])
        row = result.fetchall()

        # If there were no results return an empty dictionary
        if len(row) == 0:
            return {}

        # Format results into dictionary format
        row = row[0]
        for i in range(len(row)):
            formatted_result.update({col_names[i]: row[i]})
        return formatted_result
    return formatted_result


# For stored procedures that return a number of single value rows
def unpack_list(stored_results):
    results = []
    for result in stored_results:
        for row in result.fetchall():
            for val in row:
                results.append(val)
    return results