from fastapi import FastAPI
from api.invoice_api import router as invoice_router  # Import API hóa đơn
import modules.database as db  # Kết nối database

# Khởi tạo FastAPI
app = FastAPI(title="E-Invoice API", version="1.0")

# Đăng ký API route
app.include_router(invoice_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "🚀 Backend đang chạy thành công!"}

# Chạy server mà không cần uvicorn
def run():
    import threading
    import http.server
    import socketserver

    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 API Backend đang chạy tại http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run()
