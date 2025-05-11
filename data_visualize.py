import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

def load_csv():
    file_path = filedialog.askopenfilename()
    if file_path:
        data = pd.read_csv(file_path)
        create_plots(data)

def create_plots(data):
    for widget in frame.winfo_children():
        widget.destroy()

    fig_size = (4, 3)

    # Pie Chart
    fig1, ax1 = plt.subplots(figsize=fig_size)
    result_counts = data['game_result'].value_counts()
    ax1.pie(result_counts, labels=result_counts.index, autopct='%1.1f%%')
    ax1.set_title("Game Results")
    canvas1 = FigureCanvasTkAgg(fig1, master=frame)
    canvas1.draw()
    canvas1.get_tk_widget().grid(row=0, column=0, padx=5, pady=5)

    # Score Histogram
    # Score Box Plot
    # Score Histogram
    fig2, ax2 = plt.subplots(figsize=fig_size)
    ax2.hist(data['score'], bins=10, color='skyblue')
    ax2.set_title("Score Distribution")
    ax2.set_xlabel("Score")
    ax2.set_ylabel("Frequency")
    canvas2 = FigureCanvasTkAgg(fig2, master=frame)
    canvas2.draw()
    canvas2.get_tk_widget().grid(row=0, column=1, padx=5, pady=5)



    # Scatter: Total Moves vs Time
    fig3, ax3 = plt.subplots(figsize=fig_size)
    ax3.scatter(data['total_move'], data['time'], color='green')
    ax3.set_title("Total Moves vs Time")
    ax3.set_xlabel("Total Moves")
    ax3.set_ylabel("Time (s)")
    canvas3 = FigureCanvasTkAgg(fig3, master=frame)
    canvas3.draw()
    canvas3.get_tk_widget().grid(row=0, column=2, padx=5, pady=5)

    # Power-ups Line
    # Power-ups Collected vs Game Result
    fig4, ax4 = plt.subplots(figsize=fig_size)
    sns.stripplot(x='game_result', y='power-up_collected', data=data, ax=ax4, jitter=True, palette='Set2')
    ax4.set_title("Power-ups Collected by Game Result")
    ax4.set_xlabel("Game Result")
    ax4.set_ylabel("Power-ups Collected")
    canvas4 = FigureCanvasTkAgg(fig4, master=frame)
    canvas4.draw()
    canvas4.get_tk_widget().grid(row=1, column=0, padx=5, pady=5)


    # Score Stats Table
    # Score Statistics Table (with larger font)
    fig5, ax5 = plt.subplots(figsize=(fig_size[0], 2)) 
    ax5.axis('tight')
    ax5.axis('off')
    table_data = data['score'].describe().round(2).to_frame().T
    table = ax5.table(cellText=table_data.values, colLabels=table_data.columns, loc='center', cellLoc='center')

    
    table.auto_set_font_size(False)
    table.set_fontsize(8)  
    table.scale(1.2, 1.5)  

    canvas5 = FigureCanvasTkAgg(fig5, master=frame)
    canvas5.draw()
    canvas5.get_tk_widget().grid(row=1, column=1, padx=5, pady=5)


# Main Window
root = tk.Tk()
root.title("Game Data Analysis")

# Make window resizable
root.geometry("1200x800")
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Scrollable Canvas Frame setup
canvas = tk.Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(root, command=canvas.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
canvas.configure(yscrollcommand=scrollbar.set)

frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")

def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

frame.bind("<Configure>", on_frame_configure)

# Load CSV Button
button = tk.Button(root, text="Load CSV", command=load_csv)
button.pack()

root.mainloop()
