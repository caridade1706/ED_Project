from flask import Flask, render_template, jsonify
import pandas as pd
import os

app = Flask(__name__)

dataframes = []
websites = []

for file in os.listdir('../Scraped_Results/'):
    if file.endswith(".csv"):

        df = pd.read_csv(f'../Scraped_Results/{file}')
        df['price'] = df['price'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M%S')
        
        for website in df['website']:
            if website not in websites:
                websites.append(website)
        
        # Adicionar a coluna 'category' com base no nome do arquivo
        if 'Telemóvel' in file:
            df['category'] = 'Telemóvel'
        elif 'Smartphone' in file:
            df['category'] = 'Smartphone'
        elif 'Portáteis' in file:
            df['category'] = 'Portáteis'
        elif 'Portátil' in file :
            df['category'] = 'Portátil'
        elif 'Computadores' in file:
            df['category'] = 'Computadores'
        elif 'Computador' in file:
            df['category'] = 'Computador'
        elif 'Wireless' in file:
            df['category'] = 'Wireless'

        dataframes.append(df)

# Combinar todos os DataFrames em um único
all_data = pd.concat(dataframes, ignore_index=True)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/price-analysis")
def price_analysis():

    count_products = {}

    for website in websites:
        count_products[website] = len(all_data[all_data['website'] == website])

    return render_template("price_analysis.html", count_products=count_products)

@app.route("/categories")
def categories():
    return render_template("categories.html")

@app.route("/comparisons")
def comparisons():
    return render_template("comparisons.html")

@app.route("/api/data")
def get_data():
    # Converte os dados para JSON

    data = {
        "data": all_data.to_dict(orient="records"),
        "websites": websites
    }

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)