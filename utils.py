import matplotlib.pyplot as plt
import seaborn as sns

def show_graphs(df):
    fig1, ax1 = plt.subplots()
    df['job'].value_counts().head(5).plot(kind='bar', ax=ax1)
    ax1.set_title("Top Job Types")
    
    fig2, ax2 = plt.subplots()
    df['y'].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax2)
    ax2.set_title("Subscription Outcome")

    return fig1, fig2
