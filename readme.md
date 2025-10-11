"""
registration.py

Handles staff registration and management (view, add, update, delete) by admin.
This module no longer runs a CLI loop when executed directly. Instead it exposes a single
function `show_menu()` which prints the admin menu and handles user choices. Call
`show_menu()` from your project's `main.py` to display the registration menu.

Admin credentials (hard-coded per specification):
    name: suman rathore
    id: 100
    email: suman@gmail.com
    password: suman123

Data storage: JSON file placed in the project's `database` folder: ../database/staffs.json

Usage from main.py:
    from authentication.registration import show_menu
    show_menu()

"""

"""
menu_handling.py

Organized and colorful menu management for restaurant_management_system/domain

Features:
- Menu items: ID, Item Name, Half Rate, Full Rate
- Displays menu in a clean, table-like format
- Staff can view the menu (read-only)
- Admin can view/add/update/delete menu items
- Data stored in ../database/menu.json
- Minimum 50 predefined items with colored terminal output

Usage from main.py:
    from domain.menu_handling import show_menu
    show_menu()
"""
