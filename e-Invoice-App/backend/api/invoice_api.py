from fastapi import APIRouter
from modules.database import connect_db

router = APIRouter()

@router.get("/invoices")
def get_invoices():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM invoices;")
    invoices = cur.fetchall()
    cur.close()
    conn.close()
    return {"invoices": invoices}
