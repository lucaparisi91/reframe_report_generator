import argparse
import json
import pandas as pd

class reportGenerator: 
    def __init__(self, report):
        self.report = report

    def _get_result(self, testcase):
        if testcase["fail_phase"] == None:
            return "Passed"
        else:
            return f"Failed: {testcase['fail_phase']}"

    def _get_perfs(self,testcase):
        records=[]
        for key,value in testcase["perfvalues"].items():
            record= {
                "Variable": key.split(":")[2],
                "Value": value[0],
                "Reference": value[1],
                "Unit" : value[4] 
            }
            records.append(record)
        return records

    def generate(self, report_type="pass" ):
        data = []
        for run in self.report["runs"]:
            for testcase in run["testcases"]:

                record = {
                    "name": testcase["display_name"],
                    "jobid": testcase["jobid"]
                }

                if report_type == "pass":
                    record.update( {"result": self._get_result(testcase)   })

                data.append(record)

                self._get_perfs(testcase)


        return pd.DataFrame(data)


if __name__ == "__main__":

    data = []

    with open("report.json", "r") as f:
        j=json.load(f)

    reporter = reportGenerator(j)
    data= reporter.generate(report_type="pass")
    print(data.to_csv(sep=" "))