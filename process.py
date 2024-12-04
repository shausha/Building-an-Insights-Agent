import json
import sqlite3

def load_json(file_path):
    with open(file_path, "r") as file:
        return json.load(file)

def init_db():
    conn = sqlite3.connect("insights.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Invoices (
            id INTEGER PRIMARY KEY, 
            vendor_name TEXT, 
            contract_name TEXT, 
            invoice_number INTEGER,
            total_claimed_amount REAL,
            balance_to_finish_including_retainage REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Attachments (
            id INTEGER PRIMARY KEY, 
            invoice_id INTEGER, 
            url TEXT, 
            filename TEXT,
            FOREIGN KEY(invoice_id) REFERENCES Invoices(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Items (
            id INTEGER PRIMARY KEY, 
            invoice_id INTEGER, 
            description_of_work TEXT, 
            net_amount REAL, 
            gross_amount REAL,
            FOREIGN KEY(invoice_id) REFERENCES Invoices(id)
        )
    """)

    conn.commit()
    conn.close()

def insert_data(data):
    conn = sqlite3.connect("insights.db")
    cursor = conn.cursor()

    for invoice in data:
        cursor.execute("""
            INSERT INTO Invoices (id, vendor_name, contract_name, invoice_number, total_claimed_amount, balance_to_finish_including_retainage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            invoice["id"],
            invoice["vendor_name"],
            invoice["contract_name"],
            invoice["invoice_number"],
            invoice["total_claimed_amount"],
            invoice["summary"]["balance_to_finish_including_retainage"]
        ))

        for attachment in invoice.get("attachments", []):
            cursor.execute("""
                INSERT INTO Attachments (id, invoice_id, url, filename)
                VALUES (?, ?, ?, ?)
            """, (
                attachment["id"],
                invoice["id"],
                attachment["url"],
                attachment["filename"]
            ))
        for item in invoice.get("items", []):
            cursor.execute("""
                INSERT INTO Items (id, invoice_id, description_of_work, net_amount, gross_amount)
                VALUES (?, ?, ?, ?, ?)
            """, (
                item["id"],
                invoice["id"],
                item["description_of_work"],
                item["net_amount"],
                item["gross_amount"]
            ))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    file_path = "invoices.json"  
    data = load_json(file_path)
    init_db()
    insert_data(data)

    print("Data successfully loaded into the database.")
