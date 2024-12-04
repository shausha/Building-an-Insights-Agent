from fastapi import FastAPI, HTTPException
import sqlite3

app = FastAPI()

def get_db_connection():
    conn = sqlite3.connect("insights.db")
    conn.row_factory = sqlite3.Row  
    return conn

@app.get("/")
def home():
    return {"message": "Welcome to the Insights Agent API!"}

@app.get("/invoices/top5")
def get_top_5_invoices():
    """List the Top 5 invoices based on the original contracted amount."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, vendor_name, contract_name, invoice_number, total_claimed_amount
        FROM Invoices
        ORDER BY total_claimed_amount DESC
        LIMIT 5
    """)
    invoices = cursor.fetchall()
    conn.close()

    if not invoices:
        raise HTTPException(status_code=404, detail="No invoices found.")

    return {"top_5_invoices": [dict(invoice) for invoice in invoices]}

@app.get("/invoices/highest-balance")
def get_invoice_highest_balance():
    """Get a summary of the invoice with the highest balance to finish work."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, vendor_name, contract_name, invoice_number, balance_to_finish_including_retainage
        FROM Invoices
        ORDER BY balance_to_finish_including_retainage DESC
        LIMIT 1
    """)
    invoice = cursor.fetchone()
    conn.close()

    if not invoice:
        raise HTTPException(status_code=404, detail="No invoice found.")

    return {"highest_balance_invoice": dict(invoice)}

@app.get("/attachments/{invoice_id}")
def get_attachments(invoice_id: int):
    """Get all attachments for a given invoice."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, url, filename
        FROM Attachments
        WHERE invoice_id = ?
    """, (invoice_id,))
    attachments = cursor.fetchall()
    conn.close()

    if not attachments:
        raise HTTPException(status_code=404, detail="No attachments found for this invoice.")

    return {"attachments": [dict(attachment) for attachment in attachments]}

@app.get("/items/{invoice_id}")
def get_items(invoice_id: int):
    """Get all items for a given invoice."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, description_of_work, net_amount, gross_amount
        FROM Items
        WHERE invoice_id = ?
    """, (invoice_id,))
    items = cursor.fetchall()
    conn.close()

    if not items:
        raise HTTPException(status_code=404, detail="No items found for this invoice.")

    return {"items": [dict(item) for item in items]}