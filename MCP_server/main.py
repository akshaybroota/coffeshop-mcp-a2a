
import os
import json
from fastapi import FastAPI, HTTPException, Query
from fastmcp import FastMCP
import uvicorn
from pydantic import BaseModel
from starlette.middleware import sessions
from typing import List, Optional

SessionMiddleware = sessions.SessionMiddleware
# Session secret key for security purposes
SESSION_SECRET_KEY = "b7f8c2e1a9d4f6e3b5a1c7d8e2f4a6b9"

mcp = FastMCP(name="CoffeeShopAPI")
mcp_app = mcp.http_app(path="/mcp")

app = FastAPI(title="Fake Coffee Shop API", lifespan=mcp_app.lifespan)
app.mount("/mcp-server", mcp_app)
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

# Sample menu data
MENU_ITEMS = [
    {"id": 1, "name": "Espresso", "price": 2.5,
        "description": "Strong and bold espresso shot."},
    {"id": 2, "name": "Cappuccino", "price": 3.0,
        "description": "Espresso with steamed milk and foam."},
    {"id": 3, "name": "Latte", "price": 3.5,
        "description": "Smooth espresso with steamed milk."},
    {"id": 4, "name": "Mocha", "price": 4.0,
        "description": "Espresso with chocolate and steamed milk."},
    {"id": 5, "name": "Americano", "price": 2.0,
        "description": "Espresso with hot water."},
]

class MenuItem(BaseModel):
    id: int
    name: str
    price: float
    description: str

class ReservationRequest(BaseModel):
    name: str
    time: str  # In a real app, use datetime
    guests: int

class ReservationResponse(BaseModel):
    message: str
    reservation_id: int

@mcp.tool
@app.get("/menu", response_model=List[MenuItem])
def get_all_menu_items():
    """Get all menu items."""
    return MENU_ITEMS

@mcp.tool
@app.get("/menu/search", response_model=List[MenuItem])
def search_specific_menu_item(query: str = Query(..., description="Search term for menu item name")):
    """Search for a specific menu item by name (case-insensitive substring match)."""
    results = [item for item in MENU_ITEMS if query.lower()
               in item["name"].lower()]
    if not results:
        raise HTTPException(
            status_code=404, detail="No menu items found matching your search.")
    return results

RESERVATION_FILE = "reservations.json"

def load_reservations():
    if not os.path.exists(RESERVATION_FILE):
        return []
    with open(RESERVATION_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_reservations(reservations):
    with open(RESERVATION_FILE, "w", encoding="utf-8") as f:
        json.dump(reservations, f, indent=2)

@mcp.tool
@app.post("/reservation", response_model=ReservationResponse)
def book_a_reservation(reservation: ReservationRequest):
    """Book a reservation at the coffee shop and store it in a JSON file."""
    reservations = load_reservations()
    # Generate a unique reservation_id
    reservation_id = (max([r.get("reservation_id", 0)
                      for r in reservations]) + 1) if reservations else 1
    reservation_record = {
        "reservation_id": reservation_id,
        "name": reservation.name,
        "time": reservation.time,
        "guests": reservation.guests
    }
    reservations.append(reservation_record)
    save_reservations(reservations)
    return ReservationResponse(
        message=f"Reservation for {reservation.name} at {reservation.time} for {reservation.guests} guests confirmed!",
        reservation_id=reservation_id
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)