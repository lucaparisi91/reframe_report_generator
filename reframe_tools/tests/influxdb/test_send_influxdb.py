from reframe_tools.influxdb import send_report
import os
import json 
from reframe_tools.table_generator import TableGenerator


def test_send_report():
    "Tests sending an example report to InfluxDB database. The report is contained as a json file."

    report_file = os.path.join(os.path.dirname(__file__), "reportvprod.json")

    label = "prod" 

    with open(report_file, "r") as f:
        j = json.load(f)

    data = TableGenerator(j).generate(report_type="performance")
    print(data)

    connection_details = {
        "url": "http://localhost:8086",
        "org": "epcc",
        "token": "JTfObNAAjma5N0tNRFxI7NZIQO3VRLNxCq7dilnHOi43TXnMDmY2RLvgStLSnJ2hUTcsl49hrsJHu5UyfCQoDQ==",
    }

    send_report(data, bucket="reframe_data", connection_details=connection_details,label = label)

