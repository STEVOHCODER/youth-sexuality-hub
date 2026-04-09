# filename: main.py
import sqlite3
import pandas as pd
import numpy as np
from scipy.special import gamma
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn

app = FastAPI()

def init_db():
    conn = sqlite3.connect("fractional_data.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fractional_calc (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            degree_n INTEGER,
            order_alpha REAL,
            x_value REAL,
            result REAL
        )
    ''')
    
    # Generate data only if the table is empty
    cursor.execute("SELECT COUNT(*) FROM fractional_calc")
    if cursor.fetchone()[0] == 0:
        data = []
        degrees = [1, 2, 3]                 # Polynomial degrees (n)
        alphas = [0.5, 1.0, 1.5, 2.0]       # Fractional/Integer orders (alpha)
        x_values = np.linspace(1, 10, 10)   # x values from 1 to 10
        
        for n in degrees:
            for alpha in alphas:
                for x in x_values:
                    gamma_denom = gamma(n - alpha + 1)
                    
                    # Handle annihilation where Gamma approaches infinity
                    if np.isinf(gamma_denom):
                        val = 0.0
                    else:
                        coeff = gamma(n + 1) / gamma_denom
                        val = coeff * (x ** (n - alpha))
                        
                    data.append((n, alpha, x, val))
                    
        cursor.executemany('''
            INSERT INTO fractional_calc (degree_n, order_alpha, x_value, result)
            VALUES (?, ?, ?, ?)
        ''', data)
        conn.commit()
    conn.close()

# Initialize the database on startup
init_db()

@app.get("/api/pivot")
def get_pivot_data():
    conn = sqlite3.connect("fractional_data.db")
    df = pd.read_sql_query("SELECT * FROM fractional_calc", conn)
    conn.close()
    
    # Create a Pivot Table using Pandas (Aggregating the mean result across polynomial degrees)
    pivot_df = pd.pivot_table(
        df, 
        values='result', 
        index='x_value', 
        columns='order_alpha', 
        aggfunc='mean'
    ).reset_index()
    
    # Replace NaN with None so it's JSON serializable
    pivot_df = pivot_df.where(pd.notnull(pivot_df), None)
    
    # Convert keys to strings implicitly and return list of dicts
    return pivot_df.to_dict(orient='records')

# Mount the static files for frontend serving
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
