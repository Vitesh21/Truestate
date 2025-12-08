import pandas as pd
import os
import json
import numpy as np

DF = None
FILTER_OPTIONS = None

CSV_PATH_LOCAL = os.path.join(os.path.dirname(__file__), "../truestate_assignment_dataset.csv")
CSV_PATH_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../truestate_assignment_dataset.csv"))
PARQUET_PATH = os.path.join(os.path.dirname(__file__), "../../cached_data.parquet")
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../truestate.db"))

def get_csv_path():
    if os.path.exists(CSV_PATH_LOCAL): return CSV_PATH_LOCAL
    if os.path.exists(CSV_PATH_REPO): return CSV_PATH_REPO
    return CSV_PATH_REPO

CSV_PATH = get_csv_path()

COLUMN_MAPPING = {
    "Transaction ID": "TransactionID",
    "Date": "Date",
    "Customer ID": "CustomerID",
    "Customer Name": "CustomerName",
    "Phone Number": "PhoneNumber",
    "Gender": "Gender",
    "Age": "Age",
    "Product Category": "ProductCategory",
    "Tags": "Tags",
    "Quantity": "Quantity",
    "Price per Unit": "PricePerUnit",
    "Discount Percentage": "DiscountPercentage",
    "Total Amount": "TotalAmount",
    "Final Amount": "FinalAmount",
    "Payment Method": "PaymentMethod",
    "Order Status": "OrderStatus",
    "Delivery Type": "DeliveryType",
    "Store ID": "StoreID",
    "Store Location": "StoreLocation",
    "Salesperson ID": "SalespersonID",
    "Employee name": "EmployeeName", 
    "Employee Name": "EmployeeName",
    "Customer region": "CustomerRegion",
    "Customer Region": "CustomerRegion", 
    "Product ID": "ProductID",
    "Product Name": "ProductName",
    "Brand": "Brand",
    "Customer Type": "CustomerType"
}

def load_data():
    global DF, FILTER_OPTIONS
    
    if DF is not None:
        return DF

    # 1) Try parquet cache
    if os.path.exists(PARQUET_PATH):
        try:
            print("Loading data from Parquet cache...")
            DF = pd.read_parquet(PARQUET_PATH)
        except Exception as e:
            print(f"Error reading parquet: {e}")
            DF = None

    # 2) If parquet not loaded, try SQLite DB
    if DF is None and os.path.exists(DB_PATH):
        try:
            print(f"Loading data from SQLite DB: {DB_PATH}...")
            load_from_db()
        except Exception as e:
            print(f"Error loading from DB: {e}")
            DF = None

    # 3) If still not loaded, fallback to CSV
    if DF is None:
        print("Loading from CSV as fallback...")
        load_from_csv()

    print(f"Data Loaded: {len(DF)} rows")
    compute_filter_options()
    return DF

def load_from_csv():
    global DF
    print(f"Loading data from CSV: {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    df = df.rename(columns=COLUMN_MAPPING)
    
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    for col in ['TotalAmount', 'FinalAmount', 'PricePerUnit']:
        if col in df.columns and df[col].dtype == 'object':
                df[col] = df[col].replace(r'[^0-9.-]', '', regex=True).astype(float)
    
    if 'Tags' in df.columns:
            # Handle mixed delimiters (comma or pipe) and cleanup
            df['Tags'] = df['Tags'].fillna('').astype(str).apply(lambda x: [t.strip() for t in x.replace('|', ',').split(',') if t.strip()])

    df = df.fillna(np.nan).replace([np.nan], [None])
    
    DF = df
    
    try:
        print("Saving to Parquet cache...")
        df.to_parquet(PARQUET_PATH)
    except Exception as e:
        print(f"Could not save parquet: {e}")

    print(f"Data Loaded: {len(DF)} rows")
    compute_filter_options()
    return DF

def compute_filter_options():
    global FILTER_OPTIONS
    if DF is None: 
        return
    
    all_tags = set()
    if 'Tags' in DF.columns:
        sample = DF['Tags'].head(100000)
        for tags in sample:
            if isinstance(tags, list):
                all_tags.update(tags)
            elif isinstance(tags, str):
                # Fallback if parquet loaded as string representation
                try:
                    import ast
                    if tags.startswith('[') and tags.endswith(']'):
                        l = ast.literal_eval(tags)
                        all_tags.update(l)
                except:
                    pass
            
    FILTER_OPTIONS = {
        "regions": sorted(DF['CustomerRegion'].dropna().unique().tolist()) if 'CustomerRegion' in DF.columns else [],
        "productCategories": sorted(DF['ProductCategory'].dropna().unique().tolist()) if 'ProductCategory' in DF.columns else [],
        "paymentMethods": sorted(DF['PaymentMethod'].dropna().unique().tolist()) if 'PaymentMethod' in DF.columns else [],
        "tags": sorted(list(all_tags))
    }

def get_filter_options():
    if FILTER_OPTIONS is None:
        load_data()
    return FILTER_OPTIONS

def get_transactions(page=1, page_size=10, sort_field='Date', sort_dir='desc', q='', filters=None):
    load_data()
    
    filtered_df = DF
    
    if q:
        q = q.lower()
        mask = pd.Series(False, index=filtered_df.index)
        if 'CustomerName' in filtered_df.columns:
            mask |= filtered_df['CustomerName'].astype(str).str.lower().str.contains(q, na=False)
        if 'PhoneNumber' in filtered_df.columns:
            mask |= filtered_df['PhoneNumber'].astype(str).str.contains(q, na=False)
        
        filtered_df = filtered_df[mask]

    if filters:
        if isinstance(filters, str):
            try:
                filters = json.loads(filters)
            except:
                filters = {}
        
        if filters.get('customerRegions'):
            filtered_df = filtered_df[filtered_df['CustomerRegion'].isin(filters['customerRegions'])]
            
        if filters.get('genders'):
            filtered_df = filtered_df[filtered_df['Gender'].isin(filters['genders'])]
            
        if filters.get('productCategories'):
            filtered_df = filtered_df[filtered_df['ProductCategory'].isin(filters['productCategories'])]
            
        if filters.get('paymentMethods'):
            filtered_df = filtered_df[filtered_df['PaymentMethod'].isin(filters['paymentMethods'])]
            
        if filters.get('ageRange'):
            ar = filters['ageRange']
            min_a = ar.get('min', -float('inf'))
            max_a = ar.get('max', float('inf'))
            if 'Age' in filtered_df.columns:
                filtered_df = filtered_df[(filtered_df['Age'] >= min_a) & (filtered_df['Age'] <= max_a)]
        
        if filters.get('dateRange'):
            dr = filters['dateRange']
            start = pd.to_datetime(dr.get('from')) if dr.get('from') else None
            end = pd.to_datetime(dr.get('to')) if dr.get('to') else None
            
            if start:
                filtered_df = filtered_df[filtered_df['Date'] >= start]
            if end:
                filtered_df = filtered_df[filtered_df['Date'] <= end]
                
        if filters.get('tags'):
            target_tags = set(filters['tags'])
            filtered_df = filtered_df[filtered_df['Tags'].apply(lambda x: bool(set(x) & target_tags) if isinstance(x, list) else False)]

    if sort_field and sort_field in filtered_df.columns:
        ascending = (sort_dir == 'asc')
        filtered_df = filtered_df.sort_values(by=sort_field, ascending=ascending)

    total = len(filtered_df)
    start = (page - 1) * page_size
    end = start + page_size
    
    if start >= total:
        data = []
    else:
        page_df = filtered_df.iloc[start:end]
        
        page_df = page_df.copy()
        if 'Date' in page_df.columns:
             page_df['Date'] = page_df['Date'].dt.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
             
        data = json.loads(page_df.to_json(orient='records', date_format='iso'))

    return {
        "data": data,
        "page": page,
        "pageSize": page_size,
        "total": total
    }

def load_from_db():
    """Load data from SQLite database table `transactions` if present."""
    global DF
    import sqlite3
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    try:
        # Attempt to read the transactions table
        df = pd.read_sql_query('SELECT * FROM transactions', conn)
    except Exception as e:
        # If transactions table doesn't exist try to read a 'properties' table (legacy)
        try:
            df = pd.read_sql_query('SELECT * FROM properties', conn)
        except Exception:
            conn.close()
            raise e

    conn.close()

    # If the DB import sanitized column names (lowercase/underscores), try to map them back
    cols = set(df.columns)
    if 'Transaction ID' not in cols and 'transaction id' in cols:
        new_cols = {}
        for c in df.columns:
            nc = c.replace('_', ' ').title()
            new_cols[c] = nc
        df = df.rename(columns=new_cols)

    # Apply consistent COLUMN_MAPPING (rename to friendly keys)
    df = df.rename(columns=COLUMN_MAPPING)

    # Same cleaning as CSV path
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    for col in ['TotalAmount', 'FinalAmount', 'PricePerUnit']:
        if col in df.columns and df[col].dtype == 'object':
                df[col] = df[col].replace(r'[^0-9.-]', '', regex=True).astype(float)

    if 'Tags' in df.columns:
            df['Tags'] = df['Tags'].fillna('').astype(str).apply(lambda x: [t.strip() for t in x.replace('|', ',').split(',') if t.strip()])

    df = df.fillna(np.nan).replace([np.nan], [None])
    DF = df

    try:
        print("Saving DB-loaded data to Parquet cache...")
        df.to_parquet(PARQUET_PATH)
    except Exception as e:
        print(f"Could not save parquet: {e}")

    compute_filter_options()
    return DF
