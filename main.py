import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import yfinance as yf
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta
import threading
import warnings
warnings.filterwarnings("ignore", message="X does not have valid feature names")

class StockAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Market Analyzer")
        self.root.geometry("1400x800")

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.stock_symbol = tk.StringVar()
        self.period_var = tk.StringVar(value="6mo")
        self.stock_data = None
        self.predictions = None
        self.model = None

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)

        self.create_control_panel(main_frame)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, columnspan=3,
                           sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        self.create_chart_tab()
        self.create_statistics_tab()
        self.create_predictions_tab()
        self.create_raw_data_tab()

        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN)
        self.status_bar.grid(row=3, column=0, columnspan=3,
                             sticky=(tk.W, tk.E))

    def create_control_panel(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="10")
        control_frame.grid(row=0, column=0, columnspan=3,
                           sticky=(tk.W, tk.E), pady=(0,10))

        ttk.Label(control_frame, text="Stock Symbol:").grid(row=0, column=0, padx=5)
        symbol_entry = ttk.Entry(control_frame, textvariable=self.stock_symbol, width=15)
        symbol_entry.grid(row=0, column=1, padx=5)
        ttk.Label(control_frame, text="(e.g., TCS.NS, INFY.NS, AAPL)").grid(
            row=0, column=2, padx=5)

        ttk.Label(control_frame, text="Period:").grid(row=0, column=3, padx=5)
        periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
        period_combo = ttk.Combobox(control_frame, textvariable=self.period_var,
                                     values=periods, width=8)
        period_combo.grid(row=0, column=4, padx=5)

        ttk.Button(control_frame, text="Analyze",
                   command=self.analyze_stock).grid(row=0, column=5, padx=10)
        ttk.Button(control_frame, text="Clear",
                   command=self.clear_all).grid(row=0, column=6, padx=5)
        ttk.Button(control_frame, text="Export Data",
                   command=self.export_data).grid(row=0, column=7, padx=5)

    def create_chart_tab(self):
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="Price Chart")

        self.fig = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        chart_controls = ttk.Frame(self.chart_frame)
        chart_controls.pack(fill=tk.X, pady=5)

        self.show_ma_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(chart_controls, text="Show Moving Average",
                        variable=self.show_ma_var,
                        command=self.update_chart).pack(side=tk.LEFT, padx=5)

        self.show_predictions_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(chart_controls, text="Show Predictions",
                        variable=self.show_predictions_var,
                        command=self.update_chart).pack(side=tk.LEFT, padx=5)

    def create_statistics_tab(self):
        self.stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_frame, text="Statistics")

        self.stats_text = scrolledtext.ScrolledText(
            self.stats_frame, wrap=tk.WORD, width=80, height=25,
            font=("Courier", 10))
        self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_predictions_tab(self):
        self.pred_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pred_frame, text="Predictions")

        pred_controls = ttk.Frame(self.pred_frame)
        pred_controls.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(pred_controls, text="Prediction Days:").pack(side=tk.LEFT, padx=5)
        self.pred_days_var = tk.StringVar(value="5")

        pred_spinbox = ttk.Spinbox(pred_controls, from_=1, to=30,
                                   textvariable=self.pred_days_var, width=10)
        pred_spinbox.pack(side=tk.LEFT, padx=5)

        ttk.Button(pred_controls, text="Update Predictions",
                   command=self.update_predictions).pack(side=tk.LEFT, padx=10)

        self.pred_text = scrolledtext.ScrolledText(
            self.pred_frame, wrap=tk.WORD, width=60, height=20,
            font=("Courier", 10))
        self.pred_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def create_raw_data_tab(self):
        self.raw_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.raw_frame, text="Raw Data")

        tree_container = ttk.Frame(self.raw_frame)
        tree_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        vsb = ttk.Scrollbar(tree_container)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        hsb = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        self.tree = ttk.Treeview(tree_container, yscrollcommand=vsb.set,
                                 xscrollcommand=hsb.set, selectmode='browse')
        self.tree.pack(fill=tk.BOTH, expand=True)

        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)

    def analyze_stock(self):
        symbol = self.stock_symbol.get().strip()
        if not symbol:
            messagebox.showerror("Error", "Please enter a stock symbol")
            return

        self.status_bar.config(text=f"Analyzing {symbol}...")
        thread = threading.Thread(target=self._analyze_stock_thread, daemon=True)
        thread.start()

    def _analyze_stock_thread(self):
        try:
            symbol = self.stock_symbol.get()
            period = self.period_var.get()

            stock = yf.Ticker(symbol)
            self.stock_data = stock.history(period=period)

            if self.stock_data.empty:
                self.root.after(0, lambda: messagebox.showerror(
                    "Error", "Invalid Stock Symbol or No Data Available"))
                self.root.after(0, lambda: self.status_bar.config(text="Ready"))
                return

            self.stock_data['MA_20'] = (
                self.stock_data['Close'].rolling(window=20).mean()
            )
            self.stock_data = self.stock_data.reset_index()
            self.stock_data['Day'] = np.arange(len(self.stock_data))
            self.stock_data = self.stock_data.dropna()

            X = self.stock_data[['Day']]
            y = self.stock_data['Close']

            self.model = LinearRegression()
            self.model.fit(X, y)

            self.update_predictions_data()
            self.root.after(0, self.update_all_views)
            self.root.after(0, lambda: self.status_bar.config(
                text=f"Analysis complete for {symbol}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"Analysis failed: {str(e)}"))
            self.root.after(0, lambda: self.status_bar.config(text="Ready"))

    def update_predictions_data(self):
        if self.stock_data is None or self.model is None:
            return

        try:
            pred_days = int(self.pred_days_var.get())
        except ValueError:
            pred_days = 5

        future_days = np.arange(
            len(self.stock_data),
            len(self.stock_data) + pred_days
        ).reshape(-1, 1)

        self.predictions = self.model.predict(future_days)

    def update_all_views(self):
        if self.stock_data is None:
            return

        self.update_chart()
        self.update_statistics()
        self.update_predictions_display()
        self.update_raw_data()

    def update_chart(self):
        if self.stock_data is None:
            return

        self.ax.clear()

        self.ax.plot(self.stock_data['Day'], self.stock_data['Close'],
                     label='Closing Price', linewidth=2, color='blue')

        if self.show_ma_var.get():
            self.ax.plot(self.stock_data['Day'], self.stock_data['MA_20'],
                         label='20-Day Moving Average', linewidth=2, color='orange')

        if self.show_predictions_var.get() and self.predictions is not None:
            pred_days = np.arange(
                len(self.stock_data),
                len(self.stock_data) + len(self.predictions)
            )
            self.ax.plot(pred_days, self.predictions, linestyle='--',
                         label='Predicted Price', linewidth=2, color='red',
                         marker='o', markersize=4)

        self.ax.set_title(f"{self.stock_symbol.get()} Stock Analysis",
                          fontsize=14, fontweight='bold')
        self.ax.set_xlabel("Trading Days", fontsize=11)
        self.ax.set_ylabel("Price (₹)", fontsize=11)
        self.ax.legend(loc='best', fontsize=10)
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.set_facecolor('#f8f9fa')
        self.fig.patch.set_facecolor('#ffffff')
        self.canvas.draw()

    def update_statistics(self):
        if self.stock_data is None:
            return

        self.stats_text.delete(1.0, tk.END)
        close_prices = self.stock_data['Close']
        daily_returns = close_prices.pct_change().dropna()
        cumulative_return = (
            close_prices.iloc[-1] / close_prices.iloc[0] - 1
        ) * 100

        stats = f"""
{'='*60}
{'STOCK STATISTICS: ' + self.stock_symbol.get():^60}
{'='*60}

📊 BASIC STATISTICS
{'-'*60}
Current Price:           {close_prices.iloc[-1]:>10.2f}
Mean Price:              {close_prices.mean():>10.2f}
Median Price:            {close_prices.median():>10.2f}
Standard Deviation:      {close_prices.std():>10.2f}
Variance:                {close_prices.var():>10.2f}

📈 RANGE ANALYSIS
{'-'*60}
Maximum Price:           {close_prices.max():>10.2f}
Minimum Price:           {close_prices.min():>10.2f}
Price Range:             {close_prices.max() - close_prices.min():>10.2f}

📉 RETURNS ANALYSIS
{'-'*60}
Daily Return (Avg):      {daily_returns.mean() * 100:>9.3f}%
Daily Volatility:        {daily_returns.std() * 100:>9.3f}%
Cumulative Return:       {cumulative_return:>9.2f}%

📊 MOVING AVERAGES
{'-'*60}
20-Day MA:               {self.stock_data['MA_20'].iloc[-1]:>10.2f}
Price vs MA:             {((close_prices.iloc[-1] / self.stock_data['MA_20'].iloc[-1] - 1) * 100):>9.2f}%

📐 TREND ANALYSIS
{'-'*60}
Trend Coefficient:       {self.model.coef_[0]:>10.4f}
Intercept:               {self.model.intercept_:>10.2f}
R-squared Score:         {self.model.score(self.stock_data[['Day']], self.stock_data['Close']):>10.4f}

📊 VOLUME ANALYSIS
{'-'*60}
Average Volume:          {self.stock_data['Volume'].mean():>15,.0f}
Latest Volume:           {self.stock_data['Volume'].iloc[-1]:>15,.0f}

📅 PERIOD INFORMATION
{'-'*60}
Start Date:              {self.stock_data['Date'].iloc[0].strftime('%Y-%m-%d'):>15}
End Date:                {self.stock_data['Date'].iloc[-1].strftime('%Y-%m-%d'):>15}
Total Trading Days:      {len(self.stock_data):>15}

{'='*60}
"""
        self.stats_text.insert(1.0, stats)

    def update_predictions(self):
        if self.stock_data is None:
            messagebox.showwarning("Warning", "Please analyze a stock first")
            return

        self.status_bar.config(text="Updating predictions...")
        self.update_predictions_data()
        self.update_predictions_display()
        self.update_chart()
        self.status_bar.config(text="Predictions updated")

    def update_predictions_display(self):
        if self.stock_data is None or self.predictions is None:
            return

        self.pred_text.delete(1.0, tk.END)

        try:
            pred_days = int(self.pred_days_var.get())
        except ValueError:
            pred_days = 5

        last_date = self.stock_data['Date'].iloc[-1]

        pred_text = f"""
{'='*60}
{'PRICE PREDICTIONS FOR ' + self.stock_symbol.get():^60}
{'='*60}

📈 NEXT {pred_days} DAYS PREDICTIONS
{'-'*60}
"""

        for i, price in enumerate(self.predictions):
            pred_date = last_date + timedelta(days=i+1)

            if pred_date.weekday() < 5:
                pred_text += (
                    f"Day {i+1:<2} ({pred_date.strftime('%Y-%m-%d')}): "
                    f"{price:>10.2f}\n"
                )
            else:
                while pred_date.weekday() >= 5:
                    pred_date += timedelta(days=1)
                pred_text += (
                    f"Day {i+1:<2} ({pred_date.strftime('%Y-%m-%d')}): "
                    f"{price:>10.2f} (adjusted)\n"
                )

        trend = "UPWARD 📈" if self.model.coef_[0] > 0 else "DOWNWARD 📉"
        confidence = self.model.score(
            self.stock_data[['Day']], self.stock_data['Close'])

        pred_text += f"""
{'-'*60}
📊 PREDICTION METRICS
{'-'*60}
Model Confidence (R²):   {confidence:.4f}
Trend Direction:         {trend}
Daily Change Rate:       {self.model.coef_[0]:.4f}

🎯 PRICE TARGETS
{'-'*60}
Next Day Target:         {self.predictions[0]:.2f}
Week Target (5 days):    {self.predictions[min(4, len(self.predictions)-1)]:.2f}
Period Target:           {self.predictions[-1]:.2f}

⚠️ DISCLAIMER
{'-'*60}
These predictions are based on linear regression
and should be used for educational purposes only.
Past performance does not guarantee future results.

{'='*60}
"""
        self.pred_text.insert(1.0, pred_text)

    def update_raw_data(self):
        if self.stock_data is None:
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        columns = list(self.stock_data.columns)
        self.tree['columns'] = columns
        self.tree['show'] = 'headings'

        for col in columns:
            self.tree.heading(col, text=col)

            if col == 'Date':
                self.tree.column(col, width=120, anchor='center')
            elif col in ['Open', 'High', 'Low', 'Close', 'MA_20']:
                self.tree.column(col, width=100, anchor='e')
            elif col == 'Volume':
                self.tree.column(col, width=120, anchor='e')
            else:
                self.tree.column(col, width=80, anchor='center')

        for idx, (_, row) in enumerate(self.stock_data.iterrows()):
            if idx > 100:
                break

            values = []
            for col in columns:
                val = row[col]

                if isinstance(val, float):
                    values.append(f"{val:.2f}")
                elif isinstance(val, (pd.Timestamp, datetime)):
                    values.append(val.strftime('%Y-%m-%d'))
                else:
                    values.append(str(val))

            self.tree.insert('', 'end', values=values)

    def clear_all(self):
        self.stock_symbol.set("")
        self.period_var.set("6mo")
        self.stock_data = None
        self.predictions = None
        self.model = None

        self.ax.clear()
        self.ax.set_title("No Data Loaded")
        self.ax.set_xlabel("Days")
        self.ax.set_ylabel("Price")
        self.canvas.draw()

        self.stats_text.delete(1.0, tk.END)
        self.pred_text.delete(1.0, tk.END)

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.status_bar.config(text="Cleared")

    def export_data(self):
        if self.stock_data is None:
            messagebox.showwarning("Warning", "No data to export")
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ],
            initialfile=(
                f"{self.stock_symbol.get()}_analysis_"
                f"{datetime.now().strftime('%Y%m%d')}.csv"
            )
        )

        if filename:
            try:
                if filename.endswith('.csv'):
                    self.stock_data.to_csv(filename, index=False)
                elif filename.endswith('.xlsx'):
                    self.stock_data.to_excel(filename, index=False)
                else:
                    self.stock_data.to_csv(filename, index=False)

                messagebox.showinfo("Success",
                                    f"Data exported to {filename}")
                self.status_bar.config(
                    text=f"Data exported to {filename}")

            except Exception as e:
                messagebox.showerror("Error",
                                     f"Export failed: {str(e)}")
                self.status_bar.config(text="Export failed")


def main():
    root = tk.Tk()
    app = StockAnalyzerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
