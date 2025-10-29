
import os
import json
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional, Tuple

#  path:
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # report/ -> package root
DB_DIR = os.path.join(BASE_DIR, "database")
BOOKINGS_FILE = os.path.join(DB_DIR, "bookings.json")
ORDERS_FILE = os.path.join(DB_DIR, "orders.json")
MENU_FILE = os.path.join(DB_DIR, "menu.json")

try:
    from domain.validation import Validation
except Exception:
    class Validation:
        
        @staticmethod
        def non_empty(s: str) -> bool:
            return bool(s and str(s).strip())

        @staticmethod
        def parse_date(d: str) -> Optional[date]:
            for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
                try:
                    return datetime.strptime(d, fmt).date()
                except Exception:
                    continue
            return None

        @staticmethod
        def parse_datetime(s: str) -> Optional[datetime]:
            
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
                try:
                    return datetime.strptime(s, fmt)
                except Exception:
                    continue
            return None

        @staticmethod
        def is_positive_int(x) -> bool:
            try:
                return int(x) >= 0
            except Exception:
                return False

try:
    from domain.logs import Logger
except Exception:
    import datetime
    class Logger:
        def __init__(self):
            os.makedirs(DB_DIR, exist_ok=True)
            self.path = os.path.join(DB_DIR, "logs.txt")
        def _write(self, level: str, msg: str):
            ts = datetime.datetime.now().isoformat(sep=" ", timespec="seconds")
            try:
                with open(self.path, "a", encoding="utf-8") as f:
                    f.write(f"[{ts}] {level}: {msg}\n")
            except Exception:
                print(f"[{ts}] {level}: {msg}")
        def info(self, m: str): self._write("INFO", m)
        def warning(self, m: str): self._write("WARN", m)
        def error(self, m: str): self._write("ERR", m)



def _ensure_file(path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)
        except Exception:
            pass


def _safe_load_json(path: str) -> List[Dict]:
    _ensure_file(path)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f) or []
            if not isinstance(data, list):
                return []
            return data
    except Exception:
        return []


def _parse_order_timestamp(order: Dict, v: Validation) -> Optional[datetime]:
    
    candidates = []
    if "timestamp" in order and isinstance(order["timestamp"], str):
        candidates.append(order["timestamp"])
    if "created_at" in order and isinstance(order["created_at"], str):
        candidates.append(order["created_at"])
    if "time" in order and isinstance(order["time"], str):
        candidates.append(order["time"])
    
    if order.get("order") and isinstance(order["order"], dict):
        inner = order["order"]
        if "timestamp" in inner and isinstance(inner["timestamp"], str):
            candidates.append(inner["timestamp"])
        if "created_at" in inner and isinstance(inner["created_at"], str):
            candidates.append(inner["created_at"])
        
        if inner.get("menu_order_reference") and isinstance(inner["menu_order_reference"], dict):
            ref = inner["menu_order_reference"]
            for k in ("timestamp", "created_at"):
                if k in ref and isinstance(ref[k], str):
                    candidates.append(ref[k])

    
    for c in candidates:
        if hasattr(v, "parse_datetime"):
            dt = v.parse_datetime(c)
            if dt:
                return dt
        
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(c, fmt)
            except Exception:
                continue
    return None


# -------------------------
# Report class
# -------------------------
class Report:
    def __init__(self):
        self.validation = Validation()
        self.logger = Logger()
        _ensure_file(BOOKINGS_FILE)
        _ensure_file(ORDERS_FILE)
        _ensure_file(MENU_FILE)
        self.bookings = _safe_load_json(BOOKINGS_FILE)
        self.orders = _safe_load_json(ORDERS_FILE)
        self.menu = _safe_load_json(MENU_FILE)

    
    def reload(self):
        self.bookings = _safe_load_json(BOOKINGS_FILE)
        self.orders = _safe_load_json(ORDERS_FILE)
        self.menu = _safe_load_json(MENU_FILE)

    # -------------------------
    # Booking reports
    # -------------------------
    def total_bookings(self) -> int:
        try:
            self.reload()
            total = len(self.bookings)
            self.logger.info(f"Computed total bookings: {total}")
            return total
        except Exception as e:
            self.logger.error(f"Error computing total bookings: {e}")
            return 0

    def bookings_in_range(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Return bookings  within [start_date, end_date].
        Booking records expected to have 'date' in YYYY-MM-DD.
        """
        try:
            self.reload()
            out = []
            for b in self.bookings:
                try:
                    b_date = datetime.strptime(b.get("date", ""), "%Y-%m-%d").date()
                    if start_date <= b_date <= end_date:
                        out.append(b)
                except Exception:
                    continue
            return out
        except Exception as e:
            self.logger.error(f"Error filtering bookings in range: {e}")
            return []

    def monthly_bookings(self, year: int, month: int) -> int:
        try:
            start = date(year, month, 1)
            if month == 12:
                end = date(year + 1, 1, 1) - timedelta(days=1)
            else:
                end = date(year, month + 1, 1) - timedelta(days=1)
            count = len(self.bookings_in_range(start, end))
            self.logger.info(f"Monthly bookings for {year}-{month}: {count}")
            return count
        except Exception as e:
            self.logger.error(f"Error computing monthly bookings: {e}")
            return 0

    def weekly_bookings(self, ref_date: Optional[date] = None) -> int:
        
        try:
            ref = ref_date or date.today()
            start = ref - timedelta(days=ref.weekday()) 
            end = start + timedelta(days=6)  
            count = len(self.bookings_in_range(start, end))
            self.logger.info(f"Weekly bookings for week {start} to {end}: {count}")
            return count
        except Exception as e:
            self.logger.error(f"Error computing weekly bookings: {e}")
            return 0

    # -------------------------
    # Order reports
    # -------------------------
    def _orders_in_range(self, start_dt: datetime, end_dt: datetime) -> List[Dict]:
        
        try:
            self.reload()
            collected = []
            # top-level orders.json entries
            for o in self.orders:
                ts = _parse_order_timestamp(o, self.validation)
                if ts and start_dt <= ts <= end_dt:
                    collected.append(o)
            
            for b in self.bookings:
                if b.get("order"):
                    
                    if isinstance(b.get("created_at"), str):
                        try:
                            b_ts = datetime.strptime(b["created_at"], "%Y-%m-%d %H:%M:%S")
                        except Exception:
                            b_ts = None
                    else:
                        
                        try:
                            b_ts = datetime.strptime(f"{b.get('date','')} {b.get('start_time','')}", "%Y-%m-%d %H:%M")
                        except Exception:
                            b_ts = None
                    if b_ts and start_dt <= b_ts <= end_dt:
                        collected.append({"booking_ref": b.get("booking_id"), "order": b.get("order")})
            return collected
        except Exception as e:
            self.logger.error(f"Error extracting orders in range: {e}")
            return []

    def yearly_orders(self, year: int) -> int:
        try:
            start_dt = datetime(year, 1, 1)
            end_dt = datetime(year, 12, 31, 23, 59, 59)
            orders = self._orders_in_range(start_dt, end_dt)
            self.logger.info(f"Yearly orders for {year}: {len(orders)}")
            return len(orders)
        except Exception as e:
            self.logger.error(f"Error computing yearly orders: {e}")
            return 0

    def monthly_orders(self, year: int, month: int) -> int:
        try:
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                end = datetime(year, month + 1, 1) - timedelta(seconds=1)
            orders = self._orders_in_range(start, end)
            self.logger.info(f"Monthly orders for {year}-{month}: {len(orders)}")
            return len(orders)
        except Exception as e:
            self.logger.error(f"Error computing monthly orders: {e}")
            return 0

    def weekly_orders(self, ref_date: Optional[date] = None) -> int:
        try:
            ref = ref_date or date.today()
            start_date = ref - timedelta(days=ref.weekday())  # Monday
            start_dt = datetime.combine(start_date, datetime.min.time())
            end_dt = start_dt + timedelta(days=7) - timedelta(seconds=1)
            orders = self._orders_in_range(start_dt, end_dt)
            self.logger.info(f"Weekly orders for week starting {start_date}: {len(orders)}")
            return len(orders)
        except Exception as e:
            self.logger.error(f"Error computing weekly orders: {e}")
            return 0

    # -------------------------
    
    def _collect_item_counts(self, orders: List[Dict]) -> Dict[str, int]:
        
        counts: Dict[str, int] = {}
        for o in orders:
            
            candidates = []
            
            if "order" in o and isinstance(o["order"], dict):
                cand = o["order"]
                if isinstance(cand.get("menu_order_reference"), dict):
                    mr = cand["menu_order_reference"]
                    if isinstance(mr.get("items"), list):
                        candidates.extend(mr["items"])
                elif isinstance(cand.get("items"), list):
                    candidates.extend(cand["items"])
        
            if isinstance(o.get("items"), list):
                candidates.extend(o["items"])
        
            if isinstance(o.get("menu_order_reference"), dict) and isinstance(o["menu_order_reference"].get("items"), list):
                candidates.extend(o["menu_order_reference"]["items"])
            
            if isinstance(o.get("order_items"), list):
                candidates.extend(o["order_items"])

            
            for it in candidates:
            
                try:
                    if isinstance(it, dict):
                        name = it.get("name") or it.get("item") or it.get("title")
                        qty = int(it.get("qty") or it.get("quantity") or 1)
                    elif isinstance(it, (list, tuple)) and len(it) >= 2:
                        name = str(it[0])
                        qty = int(it[1]) if isinstance(it[1], int) else 1
                    else:
                        # if it's a string
                        name = str(it)
                        qty = 1
                    if not name:
                        continue
                    counts[name] = counts.get(name, 0) + max(1, qty)
                except Exception:
                    continue
        return counts

    def most_ordered_items(self, period: str = "yearly", ref_date: Optional[date] = None) -> List[Tuple[str, int]]:
        """
        period: 'yearly', 'monthly', 'weekly', 'perday', 'weekend'
        ref_date used to determine which month/week/day to consider (defaults to today)
        Returns list of (item_name, count) sorted desc
        """
        try:
            ref = ref_date or date.today()
            if period == "yearly":
                start_dt = datetime(ref.year, 1, 1)
                end_dt = datetime(ref.year, 12, 31, 23, 59, 59)
            elif period == "monthly":
                start_dt = datetime(ref.year, ref.month, 1)
                if ref.month == 12:
                    end_dt = datetime(ref.year + 1, 1, 1) - timedelta(seconds=1)
                else:
                    end_dt = datetime(ref.year, ref.month + 1, 1) - timedelta(seconds=1)
            elif period == "weekly":
                start_date = ref - timedelta(days=ref.weekday())
                start_dt = datetime.combine(start_date, datetime.min.time())
                end_dt = start_dt + timedelta(days=7) - timedelta(seconds=1)
            elif period == "perday":
                start_dt = datetime.combine(ref, datetime.min.time())
                end_dt = datetime.combine(ref, datetime.max.time())
            elif period == "weekend":
                
                start_date = ref - timedelta(days=ref.weekday())
                saturday = start_date + timedelta(days=5)
                sunday = start_date + timedelta(days=6)
                start_dt = datetime.combine(saturday, datetime.min.time())
                end_dt = datetime.combine(sunday, datetime.max.time())
            else:
            
                start_dt = datetime(ref.year, 1, 1)
                end_dt = datetime(ref.year, 12, 31, 23, 59, 59)

            orders = self._orders_in_range(start_dt, end_dt)
            counts = self._collect_item_counts(orders)
            
            items_sorted = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            self.logger.info(f"Most ordered items for {period} ({start_dt} to {end_dt}): top {len(items_sorted)}")
            return items_sorted
        except Exception as e:
            self.logger.error(f"Error computing most ordered items: {e}")
            return []

    # -------------------------
    # Payment methods usage
    # -------------------------
    def payment_methods_usage(self, start_dt: Optional[datetime] = None, end_dt: Optional[datetime] = None) -> Dict[str, int]:
        
        try:
            self.reload()
            if not start_dt:
                start_dt = datetime.min
            if not end_dt:
                end_dt = datetime.max

            counts: Dict[str, int] = {}
            
            for o in self.orders:
                
                ts = _parse_order_timestamp(o, self.validation) or datetime.min
                if not (start_dt <= ts <= end_dt):
                    continue
                pm = None
                if "payment" in o and isinstance(o["payment"], dict):
                    pm = o["payment"].get("method") or o["payment"].get("type")
                if not pm and "payment_method" in o:
                    pm = o.get("payment_method")
                if pm:
                    counts[pm] = counts.get(pm, 0) + 1

            # bookings with payment
            for b in self.bookings:
                
                try:
                    b_ts = datetime.strptime(b.get("created_at", f"{b.get('date','')} {b.get('start_time','00:00')}"), "%Y-%m-%d %H:%M:%S")
                except Exception:
                    try:
                        b_ts = datetime.strptime(f"{b.get('date','')} {b.get('start_time','')}", "%Y-%m-%d %H:%M")
                    except Exception:
                        b_ts = None
                if b_ts and not (start_dt <= b_ts <= end_dt):
                    continue
                pay = b.get("payment")
                if isinstance(pay, dict):
                    method = pay.get("method") or pay.get("payment_method")
                    if method:
                        counts[method] = counts.get(method, 0) + 1
            self.logger.info(f"Payment method usage between {start_dt} and {end_dt}: {counts}")
            return counts
        except Exception as e:
            self.logger.error(f"Error computing payment methods usage: {e}")
            return {}

    # -------------------------
    # Revenue
    # -------------------------
    def revenue_in_range(self, start_dt: datetime, end_dt: datetime) -> Dict[str, float]:
        
        try:
            self.reload()
            total = 0.0
            by_method: Dict[str, float] = {}
            orders_count = 0

            
            for o in self.orders:
                ts = _parse_order_timestamp(o, self.validation) or datetime.min
                if not (start_dt <= ts <= end_dt):
                    continue
                
                amount = 0.0
                if isinstance(o.get("total"), (int, float, str)):
                    try:
                        amount = float(o.get("total"))
                    except Exception:
                        amount = 0.0
                elif isinstance(o.get("final_total"), (int, float, str)):
                    try:
                        amount = float(o.get("final_total"))
                    except Exception:
                        amount = 0.0
                
                if amount == 0.0 and isinstance(o.get("payment"), dict):
                    try:
                        amount = float(o["payment"].get("amount", 0.0))
                    except Exception:
                        amount = 0.0
                
                if amount == 0.0 and isinstance(o.get("menu_order_reference"), dict):
                    try:
                        amount = float(o["menu_order_reference"].get("total", 0.0))
                    except Exception:
                        amount = 0.0
                if amount > 0.0:
                    orders_count += 1
                    total += amount
                    method = None
                    if isinstance(o.get("payment"), dict):
                        method = o["payment"].get("method")
                    if not method and o.get("payment_method"):
                        method = o.get("payment_method")
                    if method:
                        by_method[method] = by_method.get(method, 0.0) + amount

            # bookings with payment
            for b in self.bookings:
                
                b_ts = None
                if isinstance(b.get("created_at"), str):
                    try:
                        b_ts = datetime.strptime(b["created_at"], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        b_ts = None
                if not b_ts:
                    try:
                        b_ts = datetime.strptime(f"{b.get('date','')} {b.get('start_time','')}", "%Y-%m-%d %H:%M")
                    except Exception:
                        b_ts = None
                if not b_ts or not (start_dt <= b_ts <= end_dt):
                    continue
                pay = b.get("payment")
                if isinstance(pay, dict):
                    try:
                        amt = float(pay.get("amount", 0.0))
                    except Exception:
                        amt = 0.0
                    total += amt
                    orders_count += 1 if amt > 0 else 0
                    method = pay.get("method")
                    if method:
                        by_method[method] = by_method.get(method, 0.0) + amt
                
                if b.get("order") and isinstance(b["order"], dict):
                    ord_ref = b["order"]
                    ft = 0.0
                    if isinstance(ord_ref.get("final_total"), (int, float, str)):
                        try:
                            ft = float(ord_ref["final_total"])
                        except Exception:
                            ft = 0.0
                    if ft:
                        total += ft
                        orders_count += 1
            self.logger.info(f"Revenue from {start_dt} to {end_dt}: total={total:.2f}")
            return {"total_revenue": round(total, 2), "by_method": {k: round(v, 2) for k, v in by_method.items()}, "orders_count": orders_count}
        except Exception as e:
            self.logger.error(f"Error computing revenue: {e}")
            return {"total_revenue": 0.0, "by_method": {}, "orders_count": 0}

    # -------------------------
    #  menu
    # -------------------------
    def main(self):
        try:
            while True:
                print("\nREPORT MODULE")
                print("1. Total bookings")
                print("2. Monthly bookings")
                print("3. Weekly bookings")
                print("4. Yearly orders")
                print("5. Monthly orders")
                print("6. Weekly orders")
                print("7. Most ordered item")
                print("8. Payment methods usage")
                print("9. Generate revenue (date range)")
                print("10. Exit")
                choice = input("Choose (1-10): ").strip()
                if choice == "1":
                    total = self.total_bookings()
                    print(f"Total bookings: {total}")
                elif choice == "2":
                    y = input("Year (YYYY): ").strip()
                    m = input("Month (1-12): ").strip()
                    if not (y.isdigit() and m.isdigit()):
                        print("Invalid input.")
                    else:
                        print(f"Monthly bookings: {self.monthly_bookings(int(y), int(m))}")
                elif choice == "3":
                    ref = input("Reference date for week (YYYY-MM-DD) or leave blank for this week: ").strip()
                    if ref:
                        rd = self.validation.parse_date(ref)
                        if not rd:
                            print("Invalid date.")
                        else:
                            print(f"Weekly bookings: {self.weekly_bookings(rd)}")
                    else:
                        print(f"Weekly bookings: {self.weekly_bookings()}")
                elif choice == "4":
                    y = input("Year (YYYY): ").strip()
                    if not y.isdigit():
                        print("Invalid year.")
                    else:
                        print(f"Yearly orders: {self.yearly_orders(int(y))}")
                elif choice == "5":
                    y = input("Year (YYYY): ").strip()
                    m = input("Month (1-12): ").strip()
                    if not (y.isdigit() and m.isdigit()):
                        print("Invalid input.")
                    else:
                        print(f"Monthly orders: {self.monthly_orders(int(y), int(m))}")
                elif choice == "6":
                    ref = input("Reference date for week (YYYY-MM-DD) or leave blank for this week: ").strip()
                    if ref:
                        rd = self.validation.parse_date(ref)
                        if not rd:
                            print("Invalid date.")
                        else:
                            print(f"Weekly orders: {self.weekly_orders(rd)}")
                    else:
                        print(f"Weekly orders: {self.weekly_orders()}")
                elif choice == "7":
                    print("Choose period: yearly / monthly / weekly / perday / weekend")
                    p = input("Period: ").strip().lower()
                    ref = input("Reference date (YYYY-MM-DD) or leave blank for today: ").strip()
                    rd = self.validation.parse_date(ref) if ref else date.today()
                    if isinstance(rd, date) or rd:
                        items = self.most_ordered_items(period=p, ref_date=rd if isinstance(rd, date) else date.today())
                        if not items:
                            print("No ordered items found for the selected period.")
                        else:
                            print("Most ordered items (item : count):")
                            for name, cnt in items[:10]:
                                print(f"{name} : {cnt}")
                    else:
                        print("Invalid reference date.")
                elif choice == "8":
                    print("Optional: provide start and end date (YYYY-MM-DD) or leave blank for all time.")
                    s = input("Start date: ").strip()
                    e = input("End date: ").strip()
                    start_dt = None
                    end_dt = None
                    if s:
                        sd = self.validation.parse_date(s)
                        if not sd:
                            print("Invalid start date.")
                            continue
                        start_dt = datetime.combine(sd, datetime.min.time())
                    if e:
                        ed = self.validation.parse_date(e)
                        if not ed:
                            print("Invalid end date.")
                            continue
                        end_dt = datetime.combine(ed, datetime.max.time())
                    usage = self.payment_methods_usage(start_dt=start_dt, end_dt=end_dt)
                    if not usage:
                        print("No payment records found in the selected range.")
                    else:
                        print("Payment method usage counts:")
                        for method, cnt in usage.items():
                            print(f"{method} : {cnt}")
                elif choice == "9":
                    s = input("Start datetime (YYYY-MM-DD HH:MM) or date (YYYY-MM-DD): ").strip()
                    e = input("End datetime (YYYY-MM-DD HH:MM) or date (YYYY-MM-DD): ").strip()
                    sd = self.validation.parse_datetime(s) if hasattr(self.validation, "parse_datetime") else None
                    ed = self.validation.parse_datetime(e) if hasattr(self.validation, "parse_datetime") else None
                    if sd is None:
                        
                        sd_date = self.validation.parse_date(s)
                        if sd_date:
                            sd = datetime.combine(sd_date, datetime.min.time())
                    if ed is None:
                        ed_date = self.validation.parse_date(e)
                        if ed_date:
                            ed = datetime.combine(ed_date, datetime.max.time())
                    if sd is None or ed is None:
                        print("Invalid start or end. Use YYYY-MM-DD or YYYY-MM-DD HH:MM")
                        continue
                    rev = self.revenue_in_range(sd, ed)
                    print(f"Revenue from {sd} to {ed}: Total = {rev['total_revenue']:.2f}, Orders counted = {rev['orders_count']}")
                    print("Breakdown by payment method:")
                    for m, amt in rev["by_method"].items():
                        print(f"  {m} : {amt:.2f}")
                elif choice == "10":
                    break
                else:
                    print("Invalid choice. Choose 1-10.")
        except Exception as e:
            self.logger.error(f"Report main loop error: {e}")
            print("An error occurred in the Report module.")


if __name__ == "__main__":
    r = Report()
    try:
        r.main()
    except KeyboardInterrupt:
        print("\nExiting report module.")
    except Exception as ex:
        r.logger.error(f"Fatal error in report.__main__: {ex}")
