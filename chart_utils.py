import matplotlib.pyplot as plt
import numpy as np  # Import numpy to create arrays

def initialize_chart(N=400):
    fig, ax = plt.subplots()

    # Initialize line for prices
    prices_line, = ax.plot([], [], label='Price', color='blue')

    # Initialize scatter plots for buys and sells
    buys_scatter = ax.scatter([], [], marker='^', color='green', label='Buys')
    sells_scatter = ax.scatter([], [], marker='v', color='red', label='Sells')

    # Set up the axes
    ax.set_xlabel("Time")
    ax.set_ylabel("Price")
    ax.legend()
    ax.set_xlim(0, N - 1)
    ax.set_ylim(0, 1)  # Will be updated dynamically

    return fig, ax, prices_line, buys_scatter, sells_scatter, N

def update_chart(ax, prices_line, buys_scatter, sells_scatter, prices, buys, sells, balance, N):
    # Prepare data for plotting
    if len(prices) <= N:
        x_display = list(range(len(prices)))
        y_display = prices
        offset = 0
    else:
        x_display = list(range(N))
        y_display = prices[-N:]
        offset = len(prices) - N

    # Update price line
    prices_line.set_data(x_display, y_display)

    # Update buys scatter
    adjusted_buys = [(buy - offset, prices[buy]) for buy in buys if buy >= offset]
    if adjusted_buys:
        buys_scatter.set_offsets(adjusted_buys)
    else:
        buys_scatter.set_offsets(np.empty((0, 2)))  # Corrected line

    # Update sells scatter
    adjusted_sells = [(sell - offset, prices[sell]) for sell in sells if sell >= offset]
    if adjusted_sells:
        sells_scatter.set_offsets(adjusted_sells)
    else:
        sells_scatter.set_offsets(np.empty((0, 2)))  # Corrected line

    # Update axes limits
    ax.set_xlim(0, N - 1)
    y_min, y_max = min(y_display), max(y_display)
    y_margin = (y_max - y_min) * 0.05 if y_max != y_min else 1
    ax.set_ylim(y_min - y_margin, y_max + y_margin)

    # Update the title with the balance
    ax.set_title(f"Live Prices (Balance: {balance:.2f})")

    # Redraw the plot efficiently
    ax.figure.canvas.draw_idle()
    plt.pause(0.0001)
