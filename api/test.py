from databricks import sql as dbsql
import pandas as pd

# Configuration variables
server_hostname = ""
http_path = ""
databricks_pat = ""

# Establish connection
connection = dbsql.connect(
    server_hostname=server_hostname,
    http_path=http_path,
    access_token=databricks_pat
)

# Execute query
sql_query = "SELECT * FROM product_master.bronze.products_raw LIMIT 1"
with connection.cursor() as cursor:
    cursor.execute(sql_query)
    data = cursor.fetchall()
    cursor.execute("SHOW COLUMNS IN product_master.bronze.products_raw")
    columns = [column for column in cursor.fetchall()]
    df = pd.DataFrame(data=data, columns=columns)
    print(df)