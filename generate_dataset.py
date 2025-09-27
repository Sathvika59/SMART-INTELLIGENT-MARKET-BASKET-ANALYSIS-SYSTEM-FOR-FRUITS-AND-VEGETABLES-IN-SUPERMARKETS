import pandas as pd
import random
from datetime import datetime, timedelta

# Seasonal items
summer_items = ["Mango", "Watermelon", "Papaya", "Pineapple", "Muskmelon", "Ladyfinger", "Tomato", "Capsicum"]
winter_items = ["Apple", "Guava", "Carrot", "Cauliflower", "Spinach", "Cabbage", "Beetroot", "Green Peas"]
rainy_items = ["Banana", "Brinjal", "Bottle Gourd", "Chilli", "Pumpkin", "Radish"]
all_items = ["Potato", "Onion", "Garlic", "Ginger", "Coriander"]

# Category mapping
category_map = {
    **{item: "Fruit" for item in summer_items + winter_items + rainy_items if item not in
       ["Ladyfinger", "Tomato", "Capsicum", "Carrot", "Cauliflower", "Spinach", "Cabbage", "Beetroot",
        "Green Peas", "Brinjal", "Bottle Gourd", "Chilli", "Pumpkin", "Radish",
        "Potato", "Onion", "Garlic", "Ginger", "Coriander"]},
    **{item: "Vegetable" for item in
       ["Ladyfinger", "Tomato", "Capsicum", "Carrot", "Cauliflower", "Spinach", "Cabbage", "Beetroot",
        "Green Peas", "Brinjal", "Bottle Gourd", "Chilli", "Pumpkin", "Radish",
        "Potato", "Onion", "Garlic", "Ginger", "Coriander"]}
}

# Season mapping
season_map = {item: "Summer" for item in summer_items}
season_map.update({item: "Winter" for item in winter_items})
season_map.update({item: "Rainy" for item in rainy_items})
season_map.update({item: "All" for item in all_items})

rows = []
transaction_id = 1
num_transactions = 2000  # Change if you want more/less

for _ in range(num_transactions):
    # Random date in 2024
    random_date = datetime(2024, 1, 1) + timedelta(days=random.randint(0, 364))
    month = random_date.month

    # Pick season pool
    if month in [3, 4, 5, 6]:
        items_pool = summer_items + all_items
    elif month in [11, 12, 1, 2]:
        items_pool = winter_items + all_items
    elif month in [7, 8, 9]:
        items_pool = rainy_items + all_items
    else:
        items_pool = all_items

    # Choose 2–5 items
    chosen_items = random.sample(items_pool, random.randint(2, 5))

    for item in chosen_items:
        rows.append([
            transaction_id,
            random_date.strftime("%Y-%m-%d"),
            item,
            category_map[item],
            season_map[item]
        ])

    transaction_id += 1

# Create DataFrame
df = pd.DataFrame(rows, columns=["TransactionID", "Date", "Item", "Category", "Season"])

# Save CSV
df.to_csv("supermarket_dataset.csv", index=False)

print("✅ Dataset generated successfully: supermarket_dataset.csv")
print(df.head(10))
