#!/usr/bin/env python3
"""
Hermetic Zoho API Mock Server for Autonomous AI Development & CI Testing.
Simulates Zoho Books, Zoho Inventory, and Zoho CRM endpoints with idempotency validation.
"""

import sys
import json
import uuid
import time
from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8089
RECEIVED_IDEMPOTENCY_KEYS = set()

class ZohoMockHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json;charset=UTF-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode("utf-8"))

    def _verify_auth(self):
        auth = self.headers.get("Authorization", "")
        if not auth.startswith("Zoho-oauthtoken"):
            self._send_json(401, {"code": 14, "message": "Invalid OAuth token"})
            return False
        return True

    def do_POST(self):
        if not self._verify_auth():
            return

        idempotency_key = self.headers.get("Idempotency-Key")
        if idempotency_key:
            if idempotency_key in RECEIVED_IDEMPOTENCY_KEYS:
                # Idempotent response
                return self._send_json(200, {
                    "code": 0,
                    "message": "Idempotent duplicate request accepted without re-processing.",
                    "idempotency_key": idempotency_key
                })
            RECEIVED_IDEMPOTENCY_KEYS.add(idempotency_key)

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            body = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            body = {}

        path = self.path

        # 1. Zoho Books: Sales Orders (Cylinder IN)
        if "/api/v3/salesorders" in path:
            so_id = f"mock_so_{uuid.uuid4().hex[:12]}"
            return self._send_json(201, {
                "code": 0,
                "message": "The sales order has been created.",
                "salesorder": {
                    "salesorder_id": so_id,
                    "salesorder_number": body.get("salesorder_number", "SO-MOCK-001"),
                    "status": "confirmed",
                    "customer_id": body.get("customer_id"),
                    "total": sum(item.get("rate", 0) * item.get("quantity", 0) for item in body.get("line_items", []))
                }
            })

        # 2. Zoho Books: Stock Delivery Challans (Cylinder on Security or Rent)
        elif "/api/v3/deliverychallans" in path:
            challan_id = f"mock_dc_{uuid.uuid4().hex[:12]}"
            return self._send_json(201, {
                "code": 0,
                "message": "The delivery challan has been created.",
                "delivery_challan": {
                    "delivery_challan_id": challan_id,
                    "delivery_challan_number": body.get("delivery_challan_number", "DC-MOCK-001"),
                    "status": "delivered",
                    "customer_id": body.get("customer_id"),
                    "total": sum(item.get("rate", 0) * item.get("quantity", 0) for item in body.get("line_items", []))
                }
            })

        # 2. Zoho Books: Sales Invoices
        elif "/api/v3/invoices" in path:
            invoice_id = f"mock_inv_{uuid.uuid4().hex[:12]}"
            return self._send_json(201, {
                "code": 0,
                "message": "The invoice has been created.",
                "invoice": {
                    "invoice_id": invoice_id,
                    "invoice_number": body.get("invoice_number", "INV-MOCK-001"),
                    "status": "sent",
                    "customer_id": body.get("customer_id")
                }
            })

        # 3. Zoho Inventory: Transfer Orders
        elif "/api/v1/transferorders" in path:
            to_id = f"mock_to_{uuid.uuid4().hex[:12]}"
            return self._send_json(201, {
                "code": 0,
                "message": "Transfer order created successfully.",
                "transfer_order": {
                    "transfer_order_id": to_id,
                    "transfer_order_number": body.get("transfer_order_number", "TO-MOCK-001"),
                    "status": "transferred"
                }
            })

        self._send_json(404, {"code": 404, "message": f"Endpoint not found in mock: {path}"})

    def do_PATCH(self):
        if not self._verify_auth():
            return

        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        body = json.loads(post_data.decode("utf-8")) if post_data else {}

        # Zoho CRM Account Update
        if "/crm/v6/Accounts" in self.path:
            return self._send_json(200, {
                "data": [
                    {
                        "code": "SUCCESS",
                        "details": {"id": self.path.split("/")[-1]},
                        "message": "record updated successfully",
                        "status": "success"
                    }
                ]
            })

        self._send_json(404, {"code": 404, "message": f"Endpoint not found in mock: {self.path}"})

def run(port=PORT):
    server = HTTPServer(("127.0.0.1", port), ZohoMockHandler)
    print(f"[*] Hermetic Zoho API Mock Server listening on http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run(p)
