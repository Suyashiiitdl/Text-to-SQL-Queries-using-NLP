# -*- coding: utf-8 -*-
"""nlp_to_sql.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1WvDKiBXX9JPHdE93EgPt4Ro_rHE3H93G
"""

!pip install transformers torch
#https://huggingface.co/KN123/nl2sql/tree/main

# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("text2text-generation", model="KN123/nl2sql")

# Load model directly
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

tokenizer = AutoTokenizer.from_pretrained("KN123/nl2sql")
model = AutoModelForSeq2SeqLM.from_pretrained("KN123/nl2sql")

import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('sales.db')
cursor = conn.cursor()

# Create a table named 'sales'
cursor.execute('''
CREATE TABLE IF NOT EXISTS sales (
    product_id INTEGER PRIMARY KEY,
    color TEXT,
    size TEXT,
    category TEXT,
    item TEXT,
    price REAL,
    sales INTEGER
)
''')
conn.commit()

import random

# List of sample data to insert into the database
data = [
    ("Red", "M", "Men", "Tshirt", 19.99, 120),
    ("Blue", "L", "Women", "Pant", 29.99, 85),
    ("Green", "S", "Kid", "Shorts", 15.99, 60),
    ("Yellow", "XL", "Men", "Shoes", 39.99, 50),
]


while len(data) < 20:
    color = random.choice(["Red", "Blue", "Green", "Yellow", "Black", "White"])
    size = random.choice(["S", "M", "L", "XL"])
    category = random.choice(["Men", "Women", "Kid"])
    item = random.choice(["Tshirt", "Pant", "Shorts", "Shoes"])
    price = round(random.uniform(10, 50), 2)
    sales = random.randint(20, 150)
    data.append((color, size, category, item, price, sales))

# Insert data into the sales table
cursor.executemany('''
INSERT INTO sales (color, size, category, item, price, sales) VALUES (?, ?, ?, ?, ?, ?)
''', data)
conn.commit()

def text_to_sql(text):
    # Prepare the input text and encode it to tensor
    inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)

    # Generate SQL query using the model
    outputs = model.generate(**inputs)

    # Decode the generated ids to a SQL query
    sql_query = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return sql_query

# Test with an example
# example_text = "Show me all rows from sales where the category is Women"

example_text = input()
sql_query = text_to_sql(example_text)
print("Generated SQL Query directly from model:", sql_query)

def execute_query(query):
    cursor.execute(query)
    # Fetch all results
    rows = cursor.fetchall()
    for row in rows:
        print(row)

execute_query(sql_query)

# execute_query("SELECT * from sales")

