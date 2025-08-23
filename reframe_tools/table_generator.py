import argparse
import json
import pandas as pd
import numpy as np 

class TableGenerator:
    """ Generates a Pandas DataFrame from a JSON report for later analysis.
    
    Example usage:

    ```python
    with open("report.json") as f:
        report = json.load(f)

    df = TableGenerator(report).generate(report_type="pass")
    print(df)
    ```

    """

    def __init__(self, report: dict):
        self.report = report







    def _get_pass_result(self, testcase):
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
        """Generate a Pandas DataFrame from the report for the specified report type.
        
        A pass report includes only the test cases that passed, while a performance report includes performance metrics for all test cases.

        Args:
            report_type (str): The type of report to generate ("pass" or "performance").
        Returns:
            pd.DataFrame: A DataFrame containing the generated report.
        """

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
                    record.update( {"result": self._get_pass_result(testcase)   })
                    records.append(record)
                elif report_type == "performance":

                    for perf_record in self._get_perfs(testcase):
                        current_record = record.copy()
                        current_record.update(perf_record)
                        records.append(current_record)


        return pd.DataFrame(records)



