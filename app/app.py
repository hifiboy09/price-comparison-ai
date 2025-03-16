from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase
cred = credentials.Certificate("app/firebase_credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


# Home Route (Frontend)
@app.route('/')
def home():
    return render_template("index.html")


# Product Search Route
@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = search_products(query)
    return jsonify(results)


# Web Scraping Function to Search for Products
def search_products(query):
    search_results = []
    search_query = f"https://www.google.com/search?q={query}+price"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_query, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Scrape links and prices
    for link in soup.find_all('a', href=True):
        product_url = link['href']
        if "product" in product_url:  # This is a simple filter; refine as needed
            product_data = scrape_product_details(product_url)
            if product_data:
                search_results.append(product_data)
    return search_results


# Scrape Individual Product Details
def scrape_product_details(url):
    product_info = {}
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Example parsing logic for product title and price
    title = soup.find("h1").text if soup.find("h1") else "No title"
    price = soup.find("span", {
        "class": "price"
    }).text if soup.find("span", {"class": "price"}) else "No price"

    if title and price:
        product_info = {"title": title, "price": price, "url": url}
    return product_info


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
