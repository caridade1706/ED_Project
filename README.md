# **1. Introduction**
**Team**: Roberto Rolão de Castro, Tiago Caridade Gomes
## **Project Context**
This project focuses on analyzing the evolution of Portuguese e-commerce websites over time, tracking product availability, price variations, and product diversity. By leveraging *web scraping*, data cleaning, anomaly detection, and product title normalization, we provide insights into how e-commerce platforms evolve.

## **Objectives**
- Collect product data (titles, prices, categories, timestamps) from e-commerce websites.
- Clean and filter the data to remove irrelevant products.
- Detect price anomalies using machine learning techniques.
- Visualize price evolution over time for specific product categories.
- Develop a user-friendly interface to explore the data interactively.

# **2. Data Collection**

## **Web Scraping Process**
The project uses a customized scraping pipeline for multiple Portuguese e-commerce platforms.

### **Websites Scraped**
- **Worten**
- **Fnac**
- **MediaMarkt**
- **Kuantokusta**
- **El Corte Inglés**
- **PCDIGA**
- **Rádio Popular**

### **Pipeline Features**
- Extract product **title**, **price**, **category**, **timestamp**, and **website source**.
- Handle varying HTML structures across websites.
- Save results into structured **CSV files** for further analysis.

## **Challenges**
- Websites use different HTML structures, requiring dynamic adaptation.
- Avoid duplicate or irrelevant data during scraping.

# **3. Data Cleaning**

## **Objective**
Remove irrelevant or unrelated products (e.g., cables, chargers, accessories) to ensure accurate analysis of product prices.

## **Methodology**
1. Define **category-specific keywords** to filter irrelevant data.
   - Example for "Smartphones": *"capa"*, *"charger"*, *"bluetooth"*.

2. Apply keyword filtering on the product titles to exclude unwanted entries.

## **Results**
- Data reduced by approximately **56%**, improving focus on relevant products.
- Filtered data saved into new **CSV files** for analysis.

# **4. Price Anomaly Detection**

## **Objective**
Identify unusual price changes that may indicate errors, promotions, or irregularities.

## **Methodology**
- **Algorithm**: **Isolation Forest** (unsupervised anomaly detection).
- **Steps**:
   1. Aggregate product prices **monthly** using the mean.
   2. Train the Isolation Forest model on the resampled price data.
   3. Highlight anomalies using predictions.

## **Results**
- **Anomalies**: Outliers in the price data successfully detected and visualized.
- **Visualization**: Price trends with anomalies are clearly highlighted.


# **5. Price Evolution and Normalization**

## **Objective**
Track the evolution of product prices over time and normalize product titles for consistency.

## **Challenges**
- Product titles vary slightly across websites, causing duplicate entries.

## **Solution**
- Use **fuzzy matching** to group similar product titles.
- Library used: **RapidFuzz**

### **Results**
- Successfully grouped similar product titles.
- Price trends analyzed for **specific product categories** such as:
   - Smartphones
   - Laptops
   - Wireless Devices

- Price evolution visualized monthly for individual products and categories.


# **6. User Interface**

## **Objective**
Develop a graphical interface for exploring and visualizing the data interactively.

## **Features**
- Display **price trends** over time.
- Highlight **price anomalies** detected by the model.
- Provide filters to view data by:
   - **Category**
   - **Product**
   - **Website**
   - **Time Range**


# **7. Results Summary**

## **1. Data Collection**
- Successfully scraped product data from 7 major e-commerce platforms.
- Data saved in structured **CSV files**.

## **2. Data Cleaning**
- Removed irrelevant entries using keyword filtering.
- Reduced the dataset size by approximately **56%**.

## **3. Price Anomaly Detection**
- Detected price anomalies using **Isolation Forest**.
- Results highlighted irregular price points over time.

## **4. Price Evolution**
- Analyzed price trends for categories like *Smartphones*, *Laptops*, and *Wireless Devices*.
- Normalized product titles using **fuzzy matching**.

## **5. User Interface**
- Built an interactive dashboard for visualizing price trends and anomalies.


# **8. Conclusion**

This project successfully:
- Collected and cleaned product data from multiple Portuguese e-commerce platforms.
- Detected price anomalies using machine learning techniques.
- Tracked price evolution over time and developed a user-friendly interface.

# **9. How to run the Project**

## **Running the Jupyter Notebook**
1. Just run all the code.

## **Running the User Interface**

1. Ensure the **input CSV files** are in the `./Final` folder.
2. Go to the User Interface folder (`./UserInterface`).
2. Ensure that conda environment is activated.
3. Run the main app.py script:
   ```bash
   python3 app.py
   ```

## **Key Achievements**
- Efficient **web scraping** and data cleaning pipeline.
- Anomaly detection using **Isolation Forest**.
- Visualization of price trends with normalized product titles.