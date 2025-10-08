import json
import os
from typing import List, Dict, Optional

# Import authentication helpers from domain
from user_authentication import load_data, admin_authenticate

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "database")
MENU_FILE = os.path.join(DB_DIR, "menu.json")


class MenuItem:


    def __init__(self, id: int, dish: str, half_rate_min: int, half_rate_max: int, full_rate_min: int, full_rate_max: int, veg: bool = True):
        self.id = id
        self.dish = dish
        self.half_rate_min = half_rate_min
        self.half_rate_max = half_rate_max
        self.full_rate_min = full_rate_min
        self.full_rate_max = full_rate_max
        self.veg = veg

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "dish": self.dish,
            "half": [self.half_rate_min, self.half_rate_max],
            "full": [self.full_rate_min, self.full_rate_max],
            "veg": self.veg,
        }

    @staticmethod
    def from_dict(d: Dict) -> "MenuItem":
        return MenuItem(
            id=d["id"],
            dish=d["dish"],
            half_rate_min=d.get("half", [0, 0])[0],
            half_rate_max=d.get("half", [0, 0])[1],
            full_rate_min=d.get("full", [0, 0])[0],
            full_rate_max=d.get("full", [0, 0])[1],
            veg=d.get("veg", True),
        )

    def display(self) -> str:
        half = f"₹{self.half_rate_min}–₹{self.half_rate_max}"
        full = f"₹{self.full_rate_min}–₹{self.full_rate_max}"
        type_str = "Veg" if self.veg else "Non-Veg"
        return f"{self.id:3} | {self.dish:30} | {half:18} | {full:18} | {type_str}"


class MenuManager:

    def __init__(self):
        os.makedirs(DB_DIR, exist_ok=True)
        
        if not os.path.exists(MENU_FILE):
            self.menu: List[MenuItem] = self._default_menu()
            self.save()
        else:
            try:
                self.menu = self.load()
            except (json.JSONDecodeError, ValueError):
                
                print("Warning: menu.json is empty or invalid. Recreating with default menu.")
                self.menu = self._default_menu()
                self.save()

    def _default_menu(self) -> List[MenuItem]:
        
        items = [
            MenuItem(1, "Dal Makhani", 150, 250, 250, 400, veg=True),
            MenuItem(2, "Paneer Tikka Masala", 200, 300, 350, 500, veg=True),
            MenuItem(3, "Palak Paneer", 170, 270, 280, 430, veg=True),
            MenuItem(4, "Malai Kofta", 180, 280, 300, 450, veg=True),
            MenuItem(5, "Aloo Gobi", 120, 220, 200, 350, veg=True),
            MenuItem(6, "Chana Masala", 130, 230, 220, 380, veg=True),
            MenuItem(7, "Veg Biryani", 140, 240, 250, 400, veg=True),
            MenuItem(8, "Mushroom Manchurian", 150, 250, 250, 400, veg=True),
            MenuItem(9, "Gobi Manchurian", 130, 230, 220, 380, veg=True),
            MenuItem(10, "Butter Chicken", 250, 400, 400, 650, veg=False),
            MenuItem(11, "Chicken Tikka Masala", 250, 400, 400, 650, veg=False),
            MenuItem(12, "Tandoori Chicken", 220, 350, 350, 550, veg=False),
            MenuItem(13, "Mutton Curry", 300, 450, 500, 750, veg=False),
            MenuItem(14, "Chicken Biryani", 200, 350, 350, 600, veg=False),
            MenuItem(15, "Fish Curry", 250, 400, 400, 650, veg=False),
            MenuItem(16, "Prawn Curry", 300, 450, 500, 750, veg=False),
        ]
        return items

    def load(self) -> List[MenuItem]:
        # Read and parse menu.json, with defensive checks
        with open(MENU_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                raise ValueError("menu.json is empty")
            raw = json.loads(content)
        if not isinstance(raw, list):
            raise ValueError("menu.json does not contain a list")
        return [MenuItem.from_dict(d) for d in raw]

    def save(self):
        with open(MENU_FILE, "w") as f:
            json.dump([m.to_dict() for m in self.menu], f, indent=4)

    def list_menu(self):
        print("ID  | Dish                           | Half (approx.)     | Full (approx.)     | Type")
        print("----+--------------------------------+--------------------+--------------------+--------")
        for m in self.menu:
            print(m.display())
        print()

    def find_by_id(self, id: int) -> Optional[MenuItem]:
        for m in self.menu:
            if m.id == id:
                return m
        return None

    # Admin-only operations
    def add_dish(self, auth_data):
        if not admin_authenticate(auth_data):
            return
        try:
            new_id = int(input("Enter new dish id (number): ").strip())
        except ValueError:
            print("Invalid id.")
            return
        if self.find_by_id(new_id):
            print("Dish with this id already exists.")
            return
        name = input("Dish name: ").strip()
        try:
            half_min = int(input("Half plate min rate: ").strip())
            half_max = int(input("Half plate max rate: ").strip())
            full_min = int(input("Full plate min rate: ").strip())
            full_max = int(input("Full plate max rate: ").strip())
        except ValueError:
            print("Rates must be numbers.")
            return
        veg_input = input("Is this veg? (y/N): ").strip().lower()
        veg = veg_input == "y"
        item = MenuItem(new_id, name, half_min, half_max, full_min, full_max, veg)
        self.menu.append(item)
        self.menu.sort(key=lambda x: x.id)
        self.save()
        print(f"Dish '{name}' added successfully.")

    def update_dish(self, auth_data):
        if not admin_authenticate(auth_data):
            return
        try:
            id_ = int(input("Enter dish id to update: ").strip())
        except ValueError:
            print("Invalid id.")
            return
        item = self.find_by_id(id_)
        if not item:
            print("Dish not found.")
            return
        print("Leave blank to keep current value.")
        new_name = input(f"New name [{item.dish}]: ").strip()
        if new_name:
            item.dish = new_name
        try:
            val = input(f"Half min [{item.half_rate_min}]: ").strip()
            if val:
                item.half_rate_min = int(val)
            val = input(f"Half max [{item.half_rate_max}]: ").strip()
            if val:
                item.half_rate_max = int(val)
            val = input(f"Full min [{item.full_rate_min}]: ").strip()
            if val:
                item.full_rate_min = int(val)
            val = input(f"Full max [{item.full_rate_max}]: ").strip()
            if val:
                item.full_rate_max = int(val)
        except ValueError:
            print("Rates must be numbers. Update aborted.")
            return
        veg_input = input(f"Veg? (y/N) [{ 'y' if item.veg else 'N' }]: ").strip().lower()
        if veg_input:
            item.veg = veg_input == "y"
        self.save()
        print("Dish updated successfully.")

    def delete_dish(self, auth_data):
        if not admin_authenticate(auth_data):
            return
        try:
            id_ = int(input("Enter dish id to delete: ").strip())
        except ValueError:
            print("Invalid id.")
            return
        for i, it in enumerate(self.menu):
            if it.id == id_:
                confirm = input(f"Are you sure you want to delete '{it.dish}'? (y/N): ").strip().lower()
                if confirm == "y":
                    self.menu.pop(i)
                    self.save()
                    print("Dish deleted.")
                else:
                    print("Deletion cancelled.")
                return
        print("Dish not found.")

    
    def staff_take_order(self, auth_data):
        
        print("--- New Customer Order ---")
        
        self.list_menu()

        order = []  
        while True:
            try:
                id_choice = input("Enter dish id to add to order : ").strip()
                if not id_choice:
                    break
                id_choice = int(id_choice)
            except ValueError:
                print("Invalid id.")
                continue
            item = self.find_by_id(id_choice)
            if not item:
                print("Dish id not found.")
                continue
            portion = input("Portion - half or full? (h/f): ").strip().lower()
            if portion not in ("h", "f"):
                print("Invalid portion. Use 'h' or 'f'.")
                continue
            try:
                qty = int(input("Quantity: ").strip())
            except ValueError:
                print("Invalid quantity.")
                continue
            
            if portion == "h":
                chosen_price = (item.half_rate_min + item.half_rate_max) // 2
            else:
                chosen_price = (item.full_rate_min + item.full_rate_max) // 2
            order.append((item, portion, qty, chosen_price))
            print(f"Added {qty} x {item.dish} ({'Half' if portion=='h' else 'Full'}) at approx. ₹{chosen_price} each")

        if not order:
            print("No items ordered.")
            return
        # Print bill
        print("-- BILL ---")
        total = 0
        for it, portion, qty, price in order:
            line = price * qty
            total += line
            print(f"{it.dish:25} | {('Half' if portion=='h' else 'Full'):4} | {qty:2} x ₹{price} = ₹{line}")
        print("" + "-" * 40)
        print(f"TOTAL AMOUNT: ₹{total}")
        print("Thank you! Order recorded.")


def main():
    
    auth_data = load_data()
    manager = MenuManager()

    
    print("Restaurant Menu Management")
    print("1 - List menu")
    print("2 - Staff: take customer order")
    print("3 - Admin: add dish")
    print("4 - Admin: update dish")
    print("5 - Admin: delete dish")
    print("6 - Exit")
    print()  # space

    while True:
        choice = input("Choose option (1-6, 'm' to show menu again, 'q' to quit): ").strip().lower()
        if choice == "1":
            manager.list_menu()
        elif choice == "2":
            manager.staff_take_order(auth_data)
        elif choice == "3":
            manager.add_dish(auth_data)
        elif choice == "4":
            manager.update_dish(auth_data)
        elif choice == "5":
            manager.delete_dish(auth_data)
        elif choice == "6" or choice == "q":
            print("Goodbye!")
            break
        elif choice == "m":
            
            print("Restaurant Menu Management")
            print("1 - List menu")
            print("2 - Staff: take customer order")
            print("3 - Admin: add dish")
            print("4 - Admin: update dish")
            print("5 - Admin: delete dish")
            print("6 - Exit")
            print()
        else:
            print("Invalid choice. Type 1-6, 'm' to show menu, or 'q' to quit.")


if __name__ == "__main__":
    main()
