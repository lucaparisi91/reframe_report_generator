import matplotlib
# Set backend before importing pyplot - useful for headless environments
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def create_horizontal_bar_plot(data, labels, title="Horizontal Bar Plot", 
                              xlabel="Values", ylabel="Categories",
                              positive_color='green', negative_color='red',
                              figsize=(100, 6), grid=True, show_values=True,
                              xerr=None):
    """
    Generate a horizontal bar plot with positive and negative values in different colors.
    
    Args:
        data (array-like): Array of numerical values (can contain positive and negative values)
        labels (array-like): Array of labels for each bar
        title (str): Title of the plot
        xlabel (str): Label for x-axis
        ylabel (str): Label for y-axis
        positive_color (str): Color for positive bars (default: 'green')
        negative_color (str): Color for negative bars (default: 'red')
        figsize (tuple): Figure size as (width, height) (default: (10, 6))
        grid (bool): Whether to show grid lines (default: True)
        show_values (bool): Whether to show values on bars (default: True)
    
    Returns:
        tuple: (figure, axes) objects from matplotlib
    """
    
    # Convert to numpy arrays for easier manipulation
    data = np.array(data)
    labels = np.array(labels)
    xerr=np.array(xerr) if xerr is not None else None


    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create y positions for bars
    y_pos = np.arange(len(labels))
    
    # Create colors array based on positive/negative values
    colors = [positive_color if val >= 0 else negative_color for val in data]
    
    # Create horizontal bar plot
    bars = ax.barh(y_pos, data, color=colors, alpha=0.7, edgecolor='black', linewidth=0.5,xerr=xerr)
    
    # Customize the plot
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Add vertical line at x=0 to emphasize the separation
    ax.axvline(x=0, color='black', linewidth=1, alpha=0.8)
    

    # Add grid if requested
    if grid:
        ax.grid(True, alpha=0.3, axis='x')
    
    #ax.yaxis.set_yticklabels([])

    # # Add value labels on bars if requested
    # if show_values:
    #     for i, (bar, value) in enumerate(zip(bars, data)):
    #         # Position text based on whether value is positive or negative
    #         if value >= 0:
    #             # For positive values, place text at the end of the bar
    #             text_x = value + 0.01 * (ax.get_xlim()[1] - ax.get_xlim()[0])
    #             ha = 'left'
    #         else:
    #             # For negative values, place text at the end of the bar (left side)
    #             text_x = value - 0.01 * (ax.get_xlim()[1] - ax.get_xlim()[0])
    #             ha = 'right'
            
    #         ax.text(text_x, bar.get_y() + bar.get_height()/2, 
    #                f'{value:.2f}', ha=ha, va='center', fontweight='bold')
    
    # Invert y-axis to have first item at top
    ax.invert_yaxis()
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    return fig, ax


def create_comparison_bar_plot(dataframe, value_column, label_column,error_column=None, 
                             title="Performance Comparison", 
                             xlabel="Difference (%)", ylabel="Test Cases",
                             figsize=(12, 80)):
    """
    Create a horizontal bar plot from a pandas DataFrame, specifically designed 
    for performance comparison data.
    
    Args:
        dataframe (pd.DataFrame): DataFrame containing the data
        value_column (str): Name of the column containing numerical values
        label_column (str): Name of the column containing labels
        title (str): Title of the plot
        xlabel (str): Label for x-axis
        ylabel (str): Label for y-axis
        figsize (tuple): Figure size as (width, height)
    
    Returns:
        tuple: (figure, axes) objects from matplotlib
    """
    
    # Extract data and labels from DataFrame
    data = dataframe[value_column].values
    labels = dataframe[label_column].values
    errors = dataframe[error_column].values if error_column else None

    # Create the plot using the main function
    fig, ax = create_horizontal_bar_plot(
        data=data,
        labels=labels,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        xerr=errors,
        positive_color='lightgreen',
        negative_color='lightcoral',
        figsize=figsize,
        grid=True,
        show_values=True
    )
    
    return fig, ax



def split_data(data,max_rows=30):
    """
    Split the data into chunks of a specified maximum number of rows.
    
    Args:
        max_rows (int): Maximum number of rows per chunk
    
    Returns:
        list: List of DataFrames, each containing a chunk of the original data
    """

    return [data[i:i + max_rows] for i in range(0, len(data), max_rows)]



if __name__ == "__main__":

    data = pd.read_csv('report.txt', sep=' ') # Reading the performance data from a file 
    data.dropna(inplace=True)  # Drop rows with NaN values for plotting
    error_column ='Std Diff. 3-1 [%]'  # Specify error column 

    data = data[data[error_column] > 0]

    data_pages = [ data.head(30) ]  # Limit to first 30 rows for demonstration
    #data_pages=split_data(data,max_rows=100)

    for index_page,page in enumerate(data_pages):
        fig, ax = create_comparison_bar_plot(
            dataframe=page,
            value_column='Mean Diff. 3-1[%]',
            error_column=error_column,
            label_column='name',
            title="System Performance Comparison",
            xlabel="Performance Difference (%)"
        )
        plt.show()

        plt.savefig(f'performance_comparison_page_{index_page}.pdf', dpi=300)  # Save the figure with high resolution

