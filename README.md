📈 Stock Market Analyzer

A Python-based desktop application for analyzing historical stock market data, visualizing price trends, calculating statistical metrics, and generating basic future price predictions using Linear Regression.

🚀 Project Overview

The Stock Market Analyzer provides an easy-to-use graphical interface where users can enter a stock symbol and select a time period to analyze its historical performance.

The application fetches stock data using yFinance, processes the data with Pandas and NumPy, visualizes trends using Matplotlib, and uses Scikit-learn Linear Regression to generate basic price predictions.

Note: This project is intended for educational purposes. Stock predictions are not guaranteed to be accurate and should not be used as financial advice.

✨ Features

Analyze stocks using ticker symbols

Select analysis periods: 1mo, 3mo, 6mo, 1y, 2y, and 5y

Interactive stock price chart

20-day Moving Average

Linear Regression-based price prediction

Daily return and volatility analysis

Statistical analysis

Volume analysis

Raw stock data displayed in a table

Export data to CSV or Excel

Background processing using threading

🛠️ Technologies Used

Technology

Purpose

Python

Core programming language

Tkinter

Graphical User Interface

yFinance

Fetch historical stock market data

Pandas

Data processing

NumPy

Numerical operations

Matplotlib

Data visualization

Scikit-learn

Linear Regression

Threading

Background processing

🧠 Machine Learning

The project uses Linear Regression to identify the general trend in historical closing prices.

Input: Trading day number

Target: Stock closing price

Basic model:

Price = Slope × Day + Intercept

The trained model is used to estimate future prices.

Prediction Metrics

R² Score

Trend Direction

Daily Change Rate

Next Day Target

5-Day Target

Selected Period Target

📊 Moving Average

The application calculates a 20-Day Moving Average:

self.stock_data['MA_20'] = (
    self.stock_data['Close'].rolling(window=20).mean()
)

🖥️ Application Workflow

        User
         │
         ▼
 Enter Stock Symbol
         │
         ▼
 Select Time Period
         │
         ▼
 Fetch Data using yFinance
         │
         ▼
     Data Processing
         │
    ┌────┴────┐
    ▼         ▼
Moving      Statistical
Average     Analysis
    │         │
    └────┬────┘
         ▼
 Linear Regression
         │
         ▼
 Future Prediction
         │
         ▼
 Display Results

📂 Project Structure

Stock-Market-Analyzer/
│
├── stock_market_analyzer.py
├── README.md
└── requirements.txt

⚙️ Installation

1. Clone the Repository

git clone https://github.com/your-username/stock-market-analyzer.git
cd stock-market-analyzer

2. Install Required Libraries

pip install yfinance pandas numpy matplotlib scikit-learn openpyxl

If Tkinter is missing on Ubuntu/Zorin OS:

sudo apt install python3-tk

3. Run the Application

python3 stock_market_analyzer.py

📝 How to Use

Launch the application.

Enter a stock symbol.

Select the required time period.

Click Analyze.

View the stock price chart.

Enable or disable the 20-Day Moving Average.

View statistical information.

Select the number of prediction days.

Click Update Predictions.

View the raw stock data.

Export the data as CSV or Excel.

Example Stock Symbols

Indian Stocks

TCS.NS
INFY.NS
RELIANCE.NS
HDFCBANK.NS
ITC.NS

US Stocks

AAPL
MSFT
GOOGL
AMZN
TSLA

📤 Export

The application supports:

.csv

.xlsx

Exported data can be further analyzed using Excel or Python.

⚠️ Limitations

Linear Regression is a simple model and cannot capture complex market behavior.

Stock prices are affected by many external factors.

Predictions are based mainly on historical price trends.

The model does not consider news, market sentiment, company fundamentals, or economic conditions.

Future dates use a simplified weekday calculation and do not account for market holidays.

Past performance does not guarantee future results.

🔮 Future Improvements

Add LSTM/GRU deep-learning models

Add RSI, MACD, and Bollinger Bands

Add candlestick charts

Add real-time price updates

Add stock comparison

Add portfolio tracking

Add news and sentiment analysis

Support multiple stocks

Improve prediction models

Add database support

Create a web version using Flask or Streamlit

🎓 Project Purpose

This project demonstrates the practical application of:

Python programming

GUI development

Data collection

Data preprocessing

Statistical analysis

Data visualization

Machine Learning

Linear Regression

Financial data analysis

It is suitable as an academic project, portfolio project, or beginner-level Data Science/Machine Learning project.

👨‍💻 Author

Niranjan R
Harish K
Kishore A P
Farid Hasim S
