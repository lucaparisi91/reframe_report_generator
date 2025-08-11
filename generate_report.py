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


def aggregate_performance(data : pd.DataFrame):
    """Aggregate performance data by computing mean and standard deviation for each performance variable.
    
    Args:
        data: DataFrame containing performance data
    Returns:
        DataFrame: Aggregated performance data with mean and standard deviation for each performance variable.
    """


    key_columns = ["name", "system","environ", "Variable", "Unit"]
    aggregated_data=data.groupby(key_columns).agg(
        Mean=("Value", "mean"),
        Std=("Value", "std"),
    )

    return aggregated_data 

def compare_performance(report1, report2):
    """Compare two performance DataFrames and return a DataFrame with differences.
    
    Args:
        report1: First DataFrame containing performance data
        report2: Second DataFrame containing performance data
    Returns:
        DataFrame: Merged DataFrame with results merged. A column with relative differences in added as well

    """
    
    key_columns = ["name", "system","environ", "Variable", "Unit"]
    
    assert (report1.columns == report2.columns).all(), "Both reports must have the same columns for comparison."
    
    merged = pd.merge(report1, report2, on=key_columns, suffixes=('_1', '_2'), how='inner')
    
    
    if "Mean" in report1.columns: 
        merged["Mean_diff[%]"] = 100*(merged["Mean_2"] - merged["Mean_1"]) / merged["Mean_1"].replace(0, np.nan)
        merged["Std_diff[%]"] = 100*(np.sqrt(merged["Std_2"]**2 + merged["Std_1"]**2)) / merged["Mean_1"].replace(0, np.nan)

    else:
        merged["Value_diff"] = 100*(merged["Value_2"] - merged["Value_1"]) / merged["Value_1"].replace(0, np.nan)




    return merged


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate reports from ReFrame performance data")
    parser.add_argument("reports", nargs="+", help="JSON file containing ReFrame performance report")
    parser.add_argument("--aggregate", action="store_true",default=False, help="Aggregate performance data")
    parser.add_argument("--compare", action="store_true",default=False, help="Compare performance data")

    parser.add_argument("--type", choices=["pass", "performance"], default="pass", 
                       help="Report type: 'pass' or 'performance' (default: pass)")
    
    args = parser.parse_args()
    reports = []    
    for report_file in args.reports:
        # Load the report JSON file
        with open(report_file, "r") as f:
            j = json.load(f)
        
    
        # Create a report as a Pandas DataFrame
        reporter = reportGenerator(j)
        report = reporter.generate(report_type=args.type)

        # Aggregate data if requested and report type is performance
        if args.aggregate and args.type == "performance":
            report = aggregate_performance(report)

        reports.append(report)

    if args.compare:
        if len(reports) != 2:
            raise ValueError("Comparison requires exactly two reports.")
        comparison = compare_performance(reports[0], reports[1])
        print(comparison.to_csv(sep=" "))
    else:
        for report in reports:
            print(report.to_csv(sep=" "))
