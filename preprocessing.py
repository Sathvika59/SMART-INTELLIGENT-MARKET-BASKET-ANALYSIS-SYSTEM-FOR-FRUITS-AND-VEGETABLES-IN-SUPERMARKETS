import pandas as pd

def preprocess_dataset(file_path):
    """
    Preprocess dataset by splitting Item and Variety.
    Example: 'Mango (Alphonso)' → Item='Mango', Variety='Alphonso'
    """

    df = pd.read_csv(file_path)

    # Ensure Items column exists
    if "Items" not in df.columns:
        raise ValueError("Dataset must contain 'Items' column.")

    # Split 'Items' into Item and Variety
    def split_item(item):
        if "(" in item and ")" in item:
            base = item.split("(")[0].strip()
            variety = item.split("(")[1].replace(")", "").strip()
            return base, variety
        else:
            return item.strip(), None

    df[["Item", "Variety"]] = df["Items"].apply(lambda x: pd.Series(split_item(str(x))))

    # For rule generation → only Item
    df["Clean_Item"] = df["Item"].str.strip()

    return df
