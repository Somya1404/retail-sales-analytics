import pandas as pd

def load_sales(path="data/retail_sales.csv"):
    df = pd.read_csv(path, parse_dates=["order_date"])
    df["revenue"] = df["quantity"] * df["unit_price"] * (1 - df["discount_pct"] / 100)
    return df

def kpis(df):
    orders = df["order_id"].nunique()
    return {
        "revenue": df["revenue"].sum(),
        "orders": orders,
        "units": df["quantity"].sum(),
        "average_order_value": df["revenue"].sum() / orders if orders else 0
    }

def monthly_revenue(df):
    return df.set_index("order_date").resample("MS")["revenue"].sum().reset_index()

def customer_rfm(df):
    today = df["order_date"].max() + pd.Timedelta(days=1)
    return df.groupby("customer_id").agg(
        recency=("order_date", lambda x: (today - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("revenue", "sum")
    ).reset_index()

if __name__ == "__main__":
    sales = load_sales()
    print(kpis(sales))
