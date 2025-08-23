import argparse
import json
import pandas as pd
import numpy as np
from reframe_tools.table_generator import TableGenerator

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


def compare_performance(reports):
    """Compare two performance DataFrames and return a DataFrame with differences.
    
    Args:
        reports: List of DataFrames containing performance data
    Returns:
        DataFrame: Merged DataFrame with results merged. A column with relative differences in added as well

    """
    
    key_columns = ["name", "system","environ", "Variable", "Unit"]

    # Column names should be the same for all reports    
    for i in range(0,len(reports)-1):

        assert (reports[i].columns == reports[i+1].columns).all(), "Both reports must have the same columns for comparison."

    aggregated = "Mean" in reports[i].columns
    
    
    # Merge all reports on columns identifying the test. After merging an appendix _{i} is added to the column with results from the i-th report
    merged = pd.merge(reports[0], reports[1], on=key_columns, suffixes=('', '_2'), how='inner')
    for i in range(1,len(reports)-1):
        merged = pd.merge(merged, reports[i+1], on=key_columns, suffixes=('', f'_{i+2}'), how='inner')

    
    if aggregated:

        # Rename first column to avoid confusion
        merged.rename(columns={value: f"{value}_1" for value in ["Mean", "Std"]}, inplace=True)

        for i in range(1, len(reports ) ):

            # Calculate relative differences
            merged[f"Mean Diff. {i+1}-{1}[%]"] = 100*(merged[f"Mean_{i+1}"] - merged["Mean_1"]) / merged["Mean_1"].replace(0, np.nan)
            # Calculate standard deviation of the difference relative to the mean
            merged[f"Std Diff. {i+1}-{1} [%]"] = 100*(np.sqrt(merged[f"Std_{i+1}"]**2 + merged[f"Std_1"]**2)) / merged["Mean_1"].replace(0, np.nan)
            

    else:

        # Rename first column to avoid confusion
        merged.rename(columns={"Value": "Value_1"}, inplace=True)
        merged.rename(columns={"jobid": "jobid_1"}, inplace=True)

        for i in range(1, len(reports )):

            # Calculate relative differences
            merged[f"Value Diff. {i+1}-{1}[%]"] = 100*(merged[f"Value_{i+1}"] - merged["Value_1"]) / merged["Value_1"].replace(0, np.nan)

    return merged.reset_index()



def get_formatted_report(report, format_type="dsv"):
    """Write the report in the specified format.
    
    Args:
        report: DataFrame containing the report data
        format_type: Format type for the report, either 'dsv', 'markdown', or 'html'
    """
    
    if format_type == "dsv":
        return report.to_csv(sep=" ")
    elif format_type == "markdown":
        return report.to_markdown()
    elif format_type == "html":
        return report.to_html(index=False)
    else:
        raise ValueError("Unsupported format type. Use 'dsv', 'markdown', or 'html'.")


if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate reports from ReFrame performance data")
    parser.add_argument("reports", nargs="+", help="JSON file containing ReFrame performance report")
    parser.add_argument("--aggregate", action="store_true",default=False, help="Aggregate performance data")
    parser.add_argument("--compare", action="store_true",default=False, help="Compare performance data")

    parser.add_argument("--type", choices=["pass", "performance"], default="pass", 
                       help="Report type: 'pass' or 'performance' (default: pass)")
    parser.add_argument("--format", choices=["dsv", "markdown", "html"], default="dsv", 
                       help="Report format: 'dsv', 'markdown', or 'html' (default: dsv)")

    args = parser.parse_args()
    reports = []    
    for report_file in args.reports:
        # Load the report JSON file
        with open(report_file, "r") as f:
            j = json.load(f)
        
    
        # Create a report as a Pandas DataFrame
        report = TableGenerator(j).generate(report_type=args.type)

        # Aggregate data if requested and report type is performance
        if args.aggregate and args.type == "performance":
            report = aggregate_performance(report)

        reports.append(report)

    if args.compare:
        
        if len(reports) < 2:
            raise ValueError("Comparison requires at least two reports.")
        comparison = compare_performance(reports)

        if args.aggregate and args.type == "performance":
            print(get_formatted_report(comparison, format_type=args.format))

    else: # Print individual reports
        for report in reports:
            print(get_formatted_report(report, format_type=args.format))
