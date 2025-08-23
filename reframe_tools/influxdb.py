import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS
import pandas as pd

def send_report(data: pd.DataFrame, bucket: str , connection_details: dict, label: str = "regular"):
    
    client = influxdb_client.InfluxDBClient(
        url=connection_details["url"],
        org=connection_details["org"],
        token=connection_details["token"],
    )
    

    write_api = client.write_api(write_options=SYNCHRONOUS)


    # Iterate over every row of the dataframe and send data to InfluxDB
    for index, row in data.iterrows():

        point = influxdb_client.Point("performance").tag("environ", row["environ"]).tag("system",row["system"]).field("Variable", row["Variable"]).field("Value", row["Value"]).field("Name",row["name"] ).tag("label", label)

        write_api.write(bucket=bucket, record=point)

