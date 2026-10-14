import pandas as pd


files = {
    "Customers": "data/customers.csv",
    "Products": "data/products.csv",
    "Orders": "data/orders.csv",
    "Payments": "data/payments.csv"
}


for name, file_path in files.items():

    df = pd.read_csv(file_path)

    print("\n" + "=" * 50)

    print(name)

    print("=" * 50)

    print(
        "Rows:",
        len(df)
    )

    print(
        "Columns:",
        len(df.columns)
    )

    print(
        "Duplicate rows:",
        df.duplicated().sum()
    )

    print(
        "Missing values:",
        df.isnull().sum().sum()
    )

    print(
        "\nColumns:"
    )

    print(
        list(df.columns)
    )