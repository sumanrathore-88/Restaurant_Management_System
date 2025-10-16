import json
from pathlib import Path
from datetime import datetime
from domain.logs import setup_logger
from domain.validation import validate_nonempty
import os

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    USE_COLOR = True
except Exception:
    USE_COLOR = False

DB_DIR = Path(__file__).parents[1] / 'database'
DB_DIR.mkdir(exist_ok=True)
MENU_FILE = DB_DIR / 'menu.json'
ORDERS_FILE = DB_DIR / 'orders.json'

logger = setup_logger()


_default_menu = {
    "1": ["Butter Chicken", 150, 280, "Non-Veg"],
    "2": ["Paneer Butter Masala", 120, 220, "Veg"],
    "3": ["Dal Tadka", 80, 150, "Veg"],
    "4": ["Veg Fried Rice", 70, 130, "Veg"],
    "5": ["Chicken Biryani", 140, 260, "Non-Veg"],
    "6": ["Mutton Biryani", 170, 320, "Non-Veg"],
    "7": ["Masala Dosa", 60, 110, "Veg"],
    "8": ["Idli Sambar", 40, 70, "Veg"],
    "9": ["Vada Sambar", 45, 80, "Veg"],
    "10": ["Pav Bhaji", 70, 130, "Veg"],
    "11": ["Chole Bhature", 90, 160, "Veg"],
    "12": ["Rajma Chawal", 85, 150, "Veg"],
    "13": ["Kadhai Paneer", 130, 240, "Veg"],
    "14": ["Aloo Gobi", 80, 140, "Veg"],
    "15": ["Palak Paneer", 120, 220, "Veg"],
    "16": ["Paneer Tikka", 130, 240, "Veg"],
    "17": ["Chicken Tikka", 160, 290, "Non-Veg"],
    "18": ["Fish Curry", 180, 320, "Non-Veg"],
    "19": ["Egg Curry", 90, 160, "Non-Veg"],
    "20": ["Veg Manchurian", 90, 160, "Veg"],
    "21": ["Hakka Noodles", 80, 140, "Veg"],
    "22": ["Chicken Noodles", 100, 180, "Non-Veg"],
    "23": ["Paneer Fried Rice", 100, 180, "Veg"],
    "24": ["Momos (Veg)", 60, 100, "Veg"],
    "25": ["Momos (Chicken)", 70, 130, "Non-Veg"],
    "26": ["Spring Roll", 70, 130, "Veg"],
    "27": ["Sweet Corn Soup", 60, 110, "Veg"],
    "28": ["Tomato Soup", 55, 100, "Veg"],
    "29": ["Hot & Sour Soup", 65, 120, "Veg"],
    "30": ["Roti", 10, 20, "Veg"],
    "31": ["Naan", 25, 45, "Veg"],
    "32": ["Butter Naan", 30, 55, "Veg"],
    "33": ["Garlic Naan", 35, 60, "Veg"],
    "34": ["Plain Rice", 60, 100, "Veg"],
    "35": ["Jeera Rice", 70, 120, "Veg"],
    "36": ["Curd Rice", 70, 120, "Veg"],
    "37": ["Lemon Rice", 75, 130, "Veg"],
    "38": ["Veg Pulao", 90, 160, "Veg"],
    "39": ["Chicken Pulao", 110, 190, "Non-Veg"],
    "40": ["Paneer Pulao", 100, 180, "Veg"],
    "41": ["Mutton Curry", 190, 340, "Non-Veg"],
    "42": ["Butter Roti", 15, 30, "Veg"],
    "43": ["Tandoori Chicken", 180, 340, "Non-Veg"],
    "44": ["Grilled Sandwich", 60, 110, "Veg"],
    "45": ["Cheese Sandwich", 70, 120, "Veg"],
    "46": ["Paneer Wrap", 80, 140, "Veg"],
    "47": ["Chicken Wrap", 90, 160, "Non-Veg"],
    "48": ["Veg Burger", 70, 130, "Veg"],
    "49": ["Chicken Burger", 90, 160, "Non-Veg"],
    "50": ["French Fries", 60, 110, "Veg"],
    "51": ["Cold Coffee", 50, 90, "Drink"],
    "52": ["Masala Tea", 25, 40, "Drink"],
    "53": ["Lassi", 50, 90, "Drink"]
}


class Menu:
    def __init__(self):
        if not MENU_FILE.exists():
            MENU_FILE.write_text(json.dumps(_default_menu, indent=2))
        self.menu = json.loads(MENU_FILE.read_text())

    def save(self):
        MENU_FILE.write_text(json.dumps(self.menu, indent=2))
        logger.info('Menu saved/updated')

    def display_menu(self):
        print('\n=== Chatora Restaurant Menu ===')
        for k, v in sorted(self.menu.items(), key=lambda x: int(x[0])):
            name, half, full, category = v
            line = f"{k:>3}. {name:<25} HALF ₹{half:>3}  FULL ₹{full:>3}  [{category}]"
            if USE_COLOR:
                if category == 'Veg':
                    print(Fore.GREEN + line)
                elif category == 'Non-Veg':
                    print(Fore.RED + line)
                else:
                    print(Fore.CYAN + line)
            else:
                print(line)

    def admin_modify_menu(self):
        print('\n-- Admin Menu Modify --')
        print('1. Add Item  2. Update Item  3. Remove Item  4. View Menu  5. Back')
        choice = input('Choose: ').strip()
        if choice == '1':
            self.add_item()
        elif choice == '2':
            self.update_item()
        elif choice == '3':
            self.remove_item()
        elif choice == '4':
            self.display_menu()

    def add_item(self):
        nid = str(max(int(k) for k in self.menu.keys()) + 1)
        name = input('Item name: ').strip()
        if not validate_nonempty(name):
            print('Invalid name')
            return
        half = int(input('Half rate (₹): '))
        full = int(input('Full rate (₹): '))
        category = input('Category (Veg/Non-Veg/Drink): ').strip() or 'Veg'
        self.menu[nid] = [name, half, full, category]
        self.save()
        print('Item added')

    def update_item(self):
        iid = input('Item ID to update: ').strip()
        if iid not in self.menu:
            print('No such item')
            return
        name = input('New name (leave blank to keep): ').strip()
        half = input('New half rate (leave blank to keep): ').strip()
        full = input('New full rate (leave blank to keep): ').strip()
        category = input('New category (leave blank to keep): ').strip()
        if name:
            self.menu[iid][0] = name
        if half:
            self.menu[iid][1] = int(half)
        if full:
            self.menu[iid][2] = int(full)
        if category:
            self.menu[iid][3] = category
        self.save()
        print('Item updated')

    def remove_item(self):
        iid = input('Item ID to remove: ').strip()
        if iid in self.menu:
            del self.menu[iid]
            self.save()
            print('Item removed')
        else:
            print('Item not found')


class OrderManager:
    def __init__(self):
        if not ORDERS_FILE.exists():
            ORDERS_FILE.write_text(json.dumps({}, indent=2))
        self.orders = json.loads(ORDERS_FILE.read_text())
        self.menu = Menu()

    def save(self):
        ORDERS_FILE.write_text(json.dumps(self.orders, indent=2))

    def create_order(self, staff_id: int):
        print('\n--- Create Order ---')
        self.menu.display_menu()
        order_items = []
        while True:
            iid = input('Enter item ID (or q to finish): ').strip()
            if iid.lower() == 'q':
                break
            if iid not in self.menu.menu:
                print('Invalid item id')
                continue
            size = input('Half or Full (h/f): ').strip().lower()
            qty = int(input('Quantity: ').strip() or 1)
            name, half, full, cat = self.menu.menu[iid]
            price = half if size == 'h' else full
            order_items.append((iid, name, price, qty))
            print(f'Added {qty}x {name} @ ₹{price} each')

        if not order_items:
            print('No items ordered')
            return

        total = sum(price * qty for _, _, price, qty in order_items)
        print(f'Order total: ₹{total}')
        pay_mode = input('Payment mode — offline or online (o/off): ').strip().lower()
        if pay_mode.startswith('o'):
            paid = True
            print('Processing online payment... (simulated)')
        else:
            paid = False
            print('Offline payment to be collected')

        # generate order id
        oid = str(int(datetime.utcnow().timestamp() * 1000))
        self.orders[oid] = {
            'timestamp': datetime.utcnow().isoformat(),
            'staff_id': staff_id,
            'items': [{'id': iid, 'name': name, 'price': price, 'qty': qty} for iid, name, price, qty in order_items],
            'total': total,
            'paid': paid
        }
        self.save()
        logger.info(f'Order created: {oid} by staff {staff_id} total ₹{total} paid={paid}')
        print(f'Order placed. Order ID: {oid}')
        # print bill
        self.print_bill(oid)

    def print_bill(self, oid: str):
        if oid not in self.orders:
            print('Order not found')
            return
        rec = self.orders[oid]
        print('\n===== BILL =====')
        print(f'Order ID: {oid}')
        print(f'Date: {rec["timestamp"]}')
        for it in rec['items']:
            print(f"{it['qty']:>2} x {it['name']:<25} ₹{it['price']:>4}  Sub: ₹{it['price']*it['qty']}")
        print(f"TOTAL: ₹{rec['total']}")
        print('Payment status:', 'PAID' if rec['paid'] else 'PENDING')


if __name__ == '__main__':
    m = Menu()
    m.display_menu()


