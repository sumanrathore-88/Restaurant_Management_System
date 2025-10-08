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