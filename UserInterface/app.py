from flask import Flask, render_template, jsonify, request
import pandas as pd
from sklearn.ensemble import IsolationForest
import os
import re
from rapidfuzz import process, fuzz

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

def normalize_and_group_titles(df, title_column, threshold=85):
    """
    Normalize and group similar product titles using rapidfuzz for efficiency.
    """
    # Normalize titles
    def normalize_title(title):
        title = title.lower()
        title = re.sub(r'\s+', ' ', title.strip())
        title = re.sub(r'[^\w\s]', '', title)
        return title

    df["normalized_title"] = df[title_column].apply(normalize_title)

    # Use unique normalized titles
    unique_titles = df["normalized_title"].unique()
    title_mapping = {}

    for title in unique_titles:
        if title not in title_mapping:
            matches = process.extract(title, title_mapping.keys(), scorer=fuzz.ratio, score_cutoff=threshold)
            if matches:
                title_mapping[title] = matches[0][0]  # Map to the closest match
            else:
                title_mapping[title] = title  # No match found

    df["grouped_title"] = df["normalized_title"].map(title_mapping)
    return df

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
    """
    Render the Categories page with websites and normalized categories.
    """
    # Map and normalize categories
    category_mapping = {
        "Computador": "Computers",
        "Computadores": "Computers",
        "Portátil": "Computers",
        "Portáteis": "Computers",
        "Telemóvel": "Mobile",
        "Smartphone": "Mobile",
        "Wireless": "Wireless"
    }

    normalized_categories = set(
        category_mapping.get(category, category) for category in category_list
    )

    # Map websites to their display names
    lst_websites = []

    for website in websites:
        if website == 'fnac':
            lst_websites.append('Fnac')
        elif website == 'kuantokusta':
            lst_websites.append('Kuanto Kusta')
        elif website == 'worten':
            lst_websites.append('Worten')
        elif website == 'radiopopular':
            lst_websites.append('Radio Popular')
        elif website == 'pcdiga':
            lst_websites.append('PC Diga')
        elif website == 'elcorteingles':
            lst_websites.append('El Corte Inglés')
        elif website == 'mediamarkt':
            lst_websites.append('Media Markt')

    return render_template(
        "categories.html",
        websites=lst_websites,
        categories=sorted(normalized_categories)  # Sort for a better UI display
    )

@app.route("/productComparisons")
def product_comparisons():
    """
    Render the Product Comparisons page with products available on multiple websites.
    """
    # Step 1: Normalize and group product titles
    global all_data
    all_data = normalize_and_group_titles(all_data, title_column="title")

    common_products = all_data.groupby("grouped_title")["website"].nunique()

    common_products = common_products[common_products > 1]

    product_list = common_products.index.tolist()

    return render_template(
        "product_comparisons.html",
        products=sorted(product_list)  # Pass the sorted list to the frontend
    )

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

@app.route("/websitePriceEvolution", methods=["POST"])
def website_price_evolution():
    """
    Endpoint to return the mean price evolution for a specific website.
    """
    filters = request.json
    selected_website = filters.get("website")

    if selected_website == "Fnac":
        selected_website = "fnac"
    elif selected_website == "Kuanto Kusta":
        selected_website = "kuantokusta"
    elif selected_website == "Worten":
        selected_website = "worten"
    elif selected_website == "Radio Popular":
        selected_website = "radiopopular"
    elif selected_website == "PC Diga":
        selected_website = "pcdiga"
    elif selected_website == "El Corte Inglés":
        selected_website = "elcorteingles"
    elif selected_website == "Media Markt":
        selected_website = "mediamarkt"
    

    # Filter data based on the selected website
    website_data = all_data[all_data["website"] == selected_website]

    if website_data.empty:
        return jsonify({"message": f"No data available for {selected_website}."}), 404

    # Map categories to unified names
    category_mapping = {
        "Computador": "Computers",
        "Computadores": "Computers",
        "Portátil": "Computers",
        "Portáteis": "Computers",
        "Telemóvel": "Mobile",
        "Smartphone": "Mobile",
        "Wireless": "Wireless"
    }

    website_data.loc[:, "category"] = website_data["category"].map(category_mapping).fillna(website_data["category"])


    # Group data by time (monthly) and category, then calculate the mean price
    mean_price_data = website_data.groupby(
        [website_data['timestamp'].dt.to_period("M"), 'category']
    )['price'].mean().unstack(fill_value=0)

    # Convert time period to timestamp for easier use in the frontend
    mean_price_data.index = mean_price_data.index.to_timestamp()

    # Return the data as JSON
    response_data = {
        "labels": mean_price_data.index.strftime('%Y-%m').tolist(),  # Convert to list
        "datasets": [
            {
                "label": category,
                "data": mean_price_data[category].tolist()
            }
            for category in mean_price_data.columns
        ]
    }

    return jsonify(response_data)

@app.route("/categoryMeanPrice", methods=["POST"])
def category_mean_price():
    """
    Endpoint to return the yearly mean price evolution of a selected category across websites.
    """
    filters = request.json
    selected_category = filters.get("category")

    # Map similar categories to unified names
    category_mapping = {
        "Computador": "Computers",
        "Computadores": "Computers",
        "Portátil": "Computers",
        "Portáteis": "Computers",
        "Telemóvel": "Mobile",
        "Smartphone": "Mobile",
        "Wireless": "Wireless"
    }

    # Normalize the selected category
    normalized_category = category_mapping.get(selected_category, selected_category)

    # Filter data based on the normalized category
    filtered_data = all_data[
        all_data["category"].map(category_mapping).fillna(all_data["category"]) == normalized_category
    ].copy()  # Use `.copy()` to avoid SettingWithCopyWarning

    if filtered_data.empty:
        return jsonify({"message": f"No data available for {selected_category}."}), 404

    # Extract the year and month from the timestamp
    filtered_data.loc[:, "month"] = filtered_data["timestamp"].dt.to_period("M")  # Use .loc for assignment

    # Group by month and website, then calculate mean price
    mean_prices = filtered_data.groupby(["month", "website"])["price"].mean().unstack(fill_value=0)

    # Convert the index to timestamp for frontend compatibility
    mean_prices.index = mean_prices.index.to_timestamp()

    # Prepare the data for JSON response
    response_data = {
        "years": mean_prices.index.strftime("%Y-%m").tolist(),  # Format as strings for frontend
        "datasets": [
            {
                "label": website,
                "data": mean_prices[website].tolist()
            }
            for website in mean_prices.columns
        ],
        "category": normalized_category
    }

    return jsonify(response_data)

@app.route("/productPriceEvolution", methods=["POST"])
def product_price_evolution():
    """
    Endpoint to return the price evolution of a product across multiple websites.
    """
    filters = request.json
    selected_product = filters.get("product_name")
    
    # Filter data for the selected product and create a copy
    product_data = all_data[all_data["grouped_title"] == selected_product].copy()

    print(product_data)

    if product_data.empty:
        return jsonify({"message": f"No data available for {selected_product}."}), 404

    # Group by time (monthly) and website, then calculate mean price
    product_data["month"] = product_data["timestamp"].dt.to_period("M")
    price_evolution = product_data.groupby(["month", "website"])["price"].mean().unstack()

    # Convert the index to timestamps for the frontend
    price_evolution.index = price_evolution.index.to_timestamp()

    # Prepare the data for JSON response
    response_data = {
        "labels": price_evolution.index.strftime("%Y-%m").tolist(),
        "datasets": [
            {
                "label": website,
                "data": [None if pd.isna(value) else value for value in price_evolution[website]]
            }
            for website in price_evolution.columns
        ],
        "product_name": selected_product
    }

    return jsonify(response_data)

if __name__ == "__main__":
    app.run(debug=True)