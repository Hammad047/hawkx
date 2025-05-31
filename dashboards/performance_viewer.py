import pandas as pd
import matplotlib.pyplot as plt

# Load the performance log
log_path = "performance_log.csv"
try:
    df = pd.read_csv(log_path, names=["timestamp", "symbol", "signal", "result"], parse_dates=["timestamp"])
except Exception as e:
    df = pd.DataFrame(columns=["timestamp", "symbol", "signal", "result"])

# Fill empty results if needed
df["result"] = df["result"].fillna("UNKNOWN")

# Pie chart: Win/Loss ratio
win_loss_counts = df["result"].value_counts()
plt.figure(figsize=(6, 6))
plt.pie(win_loss_counts, labels=win_loss_counts.index, autopct='%1.1f%%', startangle=140)
plt.title("Trade Result Distribution (Win/Loss/Other)")
plt.tight_layout()
plt.show()

# Bar chart: Top performing symbols by number of WINs
top_symbols = df[df["result"] == "WIN"]["symbol"].value_counts().head(10)
plt.figure(figsize=(10, 6))
top_symbols.plot(kind='bar', color='green')
plt.title("Top Performing Symbols (by WIN count)")
plt.xlabel("Symbol")
plt.ylabel("Number of WINs")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
