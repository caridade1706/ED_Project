from flask import Flask, render_template, jsonify, request
import pandas as pd
from sklearn.ensemble import IsolationForest
import os

app = Flask(__name__)

# Load the data (once at the start for efficiency)
dataframes = []
websites = []
category_list = set()

for file in os.listdir('../Final/'):
    
    if file.endswith(".csv"):
        df = pd.read_csv(f'../Final/{file}')
        df['price'] = df['price'].astype(float)
        df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y%m%d%H%M%S')
        
        # Extract unique websites
        websites.extend(df['website'].unique())
        
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

        # Add unique categories
        category_list.update(df['category'].unique())

        dataframes.append(df)

# Combine all DataFrames into one
all_data = pd.concat(dataframes, ignore_index=True)
websites = list(set(websites))  # Remove duplicates
category_list = list(category_list)

def filter_products_with_minimum_rows(data, min_rows=3):
    """
    Filter products that have at least a minimum number of rows.
    """
    product_counts = data["title"].value_counts()
    valid_products = product_counts[product_counts >= min_rows].index
    filtered_data = data[data["title"].isin(valid_products)]
    return filtered_data


def detect_price_anomalies(data, product_name):
    """
    Detect unusual price changes for a given filtered dataset using Isolation Forest.
    """
    # Filter data for the specified product
    product_data = data[data["title"] == product_name][["timestamp", "price"]]

    if product_data.empty:
        return None

    # Prepare data
    product_data["timestamp"] = pd.to_datetime(product_data["timestamp"], format="%Y%m%d%H%M%S")
    product_data = product_data.set_index("timestamp").sort_index()
    product_data = product_data.resample("ME").mean().ffill()  # Resample monthly, forward fill

    # Apply Isolation Forest for anomaly detection
    model = IsolationForest(contamination=0.4, random_state=42)
    product_data["anomaly"] = model.fit_predict(product_data[["price"]])
    product_data["anomaly_score"] = model.decision_function(product_data[["price"]])

    # Check if anomalies are detected
    anomalies = product_data[product_data["anomaly"] == -1]

    return {
        "data": product_data.reset_index().to_dict(orient="records"),
        "anomalies": anomalies.reset_index().to_dict(orient="records"),
    }

@app.route("/")
def index():

    count_products = {}

    for website in websites:

        website_correct = None

        if website == 'fnac':
            website_correct = 'Fnac'
        elif website == 'kuantokusta':
            website_correct = 'Kuanto Kusta'
        elif website == 'worten':
            website_correct = 'Worten'
        elif website == 'radiopopular':
            website_correct = 'Radio Popular'
        elif website == 'pcdiga':
            website_correct = 'PC Diga'
        elif website == 'elcorteingles':
            website_correct = 'El Corte Inglés'
        elif website == 'mediamarkt':
            website_correct = 'Media Markt'

        # Remove duplicate products for this website based on product_name
        unique_products = all_data[all_data['website'] == website].drop_duplicates(subset='title')
        count_products[website_correct] = len(unique_products)

    print(count_products)

    return render_template("index.html",  count_products=count_products)

@app.route("/price-analysis")
def price_analysis():
    return render_template("price_analysis.html")

@app.route("/categories")
def categories():
    return render_template("categories.html")

@app.route("/priceAnomalies", methods=["GET", "POST"])
def priceAnomalies():
    if request.method == "POST":
        # Get selected filters from the user
        filters = request.json
        selected_websites = filters.get("websites", [])
        selected_categories = filters.get("categories", [])

        # Filter the data based on user selection
        filtered_data = all_data[
            all_data["website"].isin(selected_websites) &
            all_data["category"].isin(selected_categories)
        ]

        # Ensure minimum rows for anomaly detection
        filtered_data = filter_products_with_minimum_rows(filtered_data, min_rows=4)

        if filtered_data.empty:
            return jsonify({"message": "No products with sufficient data for the selected filters."}), 404

        # Detect anomalies for each product
        anomalies = []
        for product_name in filtered_data["title"].unique():
            product_anomalies = detect_price_anomalies(filtered_data, product_name)
            if product_anomalies is not None:
                anomalies.append({
                    "product_name": product_name,
                    "anomalies": product_anomalies["anomalies"],  # Access the anomalies key
                    "data": product_anomalies["data"],  # Access the data key
                })

        if not anomalies:
            return jsonify({"message": "No anomalies detected for the selected filters."}), 200

        return jsonify({"anomalies": anomalies})

    # For GET requests, render the page
    return render_template(
        "priceAnomalies.html",
        websites=websites,
        categories=category_list
    )


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