import pandas as pd
import matplotlib.pyplot as plt

def plot_pnl_distribution(csv_file):
    """
    Function to plot the distribution of trade PnL from a CSV file.

    :param csv_file: Path to the CSV file containing trade data
    """
    # Load the CSV file
    df = pd.read_csv(csv_file)

    # Filter out rows with NaN in the 'pnl' column
    pnl_df = df.dropna(subset=['pnl'])

    # Plot the distribution of trade PnL
    plt.figure(figsize=(8, 6))
    plt.hist(pnl_df['pnl'], bins=10, edgecolor='black')
    plt.title('Distribution of Trade PnL')
    plt.xlabel('PnL')
    plt.ylabel('Frequency')
    plt.grid(True)

    # Show the plot
    plt.show()
