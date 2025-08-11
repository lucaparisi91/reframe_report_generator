import argparse
import json
import pandas as pd
import numpy as np 

class reportGenerator: 
    def __init__(self, report):
        self.report = report

    def _get_result(self, testcase):
        if testcase["fail_phase"] == None:
            return "Passed"
        else:
            return f"Failed: {testcase['fail_phase']}"

    def _get_perfs(self,testcase):
        """ Extract performance values from a testcase. 
        
        Args:
            testcase (dict): A dictionary representing a single test case from the report.
        Returns:
            list: A list of dictionaries, each containing performance variable, value, reference, and unit
        """

        records=[]

        if "perfvalues" in testcase.keys():        
            for key,value in testcase["perfvalues"].items():
                
                

                record= {
                    "Variable": str(key.split(":")[2]),
                    "Unit" : str(value[4]),
                    #"Reference": np.float32(value[1]),
                    "Value": np.float32(value[0]),
                }

                records.append(record)
            return records

    def generate(self, report_type="pass" ):
        records= []
        for run in self.report["runs"]:
            for testcase in run["testcases"]:
                
                record = {
                    "name": testcase["display_name"],
                    "jobid": testcase["jobid"],
                    "system": testcase["system"],
                    "environ": testcase["environ"],
                }

                if report_type == "pass":
                    record.update( {"result": self._get_result(testcase)   })
                    records.append(record)
                elif report_type == "performance":

                    for perf_record in self._get_perfs(testcase):
                        current_record = record.copy()
                        current_record.update(perf_record)
                        records.append(current_record)


        return pd.DataFrame(records)


def aggregate_performance(data):
    key_columns = ["name", "system","environ", "Variable", "Unit"]
    aggregated_data=data.groupby(key_columns).agg(
        Mean=("Value", "mean"),
        Std=("Value", "std"),
    )

    return aggregated_data 


if __name__ == "__main__":

    data = []

    with open("report.json", "r") as f:
        j=json.load(f)
    
    reporter = reportGenerator(j)
    data= aggregate_performance( reporter.generate(report_type="performance") )
    print(data.to_csv(sep=" "))