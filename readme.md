🏪 Restaurant Management System — Staff Authentication Module

This module manages staff registration and authentication for the Restaurant Management System.  
It allows the admin to add, update, delete, search, and view staff information using a JSON-based storage system.

---


# 🍽️ Restaurant Menu Management System (`menu_handling.py`)



`menu_handling.py` is a Python-based menu management system for a restaurant.  
It allows **staff** to take customer orders and **admins** to manage the restaurant’s menu — including adding, updating, and deleting dishes — all backed by simple JSON-based storage.

The system separates staff and admin privileges using a lightweight authentication module (`user_authentication.py`).

---



Order management for Restaurant_management_system (domain/order.py)
- Staff can create and view orders.
- Only admin can modify or cancel orders (admin authentication required).
- Orders are persisted to ../database/order.json

Dependencies:
- user_authentication.py (for admin authentication and load_data)
- menu_handling.py (to look up dishes and prices)


# domain/bill.py
"""
Billing system for Restaurant_management_system
- Staff can create bills for existing orders (from ../database/order.json).
- Bills are persisted to ../database/bill.json
- Only admin can modify or cancel a bill (admin authentication required).

This module expects the following helpers in the same `domain` package:
- user_authentication.load_data and user_authentication.admin_authenticate
- order.OrderManager or direct access to order JSON (we import OrderManager here)
- menu_handling.MenuManager is optional (used for display)
"""

# domain/table_booking.py
"""
Table booking system for Restaurant_management_system
- 10 tables, each with 6 seats.
- Staff can create bookings for customers (name, contact, date, time, party size).
- Staff can view availability, check menu, create order and payment tied to a booking.
- Only admin can modify or cancel bookings after creation (admin authentication required).
- Bookings are saved to ../database/booking.json

Integrations used (expected to exist in the `domain` package):
- user_authentication.load_data and user_authentication.admin_authenticate
- menu_handling.MenuManager
- order.OrderManager (to create orders tied to a booking)
- bill.BillManager (to create bills from orders)