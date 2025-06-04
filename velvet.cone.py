import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
import random
import datetime
from fpdf import FPDF
import shutil
import os
import ast

class IceCreamShopApp:
    def load_menu_from_file(self, filename):
        menu = {}
        try:
            with open(filename, "r") as f:
                for line in f:
                    if '-' in line:
                        parts = line.strip().split('-', 1)
                        if len(parts) == 2:
                            flavor = parts[0].strip()
                            price_str = parts[1].strip()
                            try:
                                menu[flavor] = float(price_str)
                            except ValueError:
                                pass
        except FileNotFoundError:
            messagebox.showerror("Error", f"Menu file '{filename}' not found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load menu: {e}")
        return menu if menu else {"Vanilla": 100.0}

    def save_menu_to_file(self, filename, menu_dict):
        try:
            with open(filename, "w") as f:
                for flavor, price in menu_dict.items():
                    f.write(f"{flavor} - {price}\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save menu: {e}")

    def __init__(self, root):
        self.root = root
        self.root.title("Velvet Cone - Ice Cream Ordering System")
        self.root.geometry("1000x600")
        self.root.configure(bg="#E3F2FD")

        self.shop_name = "Velvet Cone"
        self.logo_img = self.create_logo()
        self.order_history = []

        self.menu_txt_file = "menu.txt"
        self.menu_items = self.load_menu_from_file(self.menu_txt_file)
        self.container_prices = {"Cup": 0, "Cone": 10}
        self.orders_file = "all_orders.txt"
        self.load_all_orders()

        self.create_widgets()

    def calculate_icecream_price(self, flavor, scoops, menu, container, container_prices):
        if flavor not in menu:
            return 0.0
        if not (1 <= scoops <= 3):
            return 0.0
        total = menu[flavor] * scoops + container_prices.get(container, 0)
        return total

    def create_logo(self):
        logo_frame = tk.Frame(self.root, bg="#E3F2FD")
        logo_frame.pack(pady=10)
        tk.Label(logo_frame, text="Velvet Cone", font=("Georgia", 28, "bold"),
                 fg="#2B2E4A", bg="#E3F2FD").pack(side=tk.LEFT, padx=10)
        return logo_frame

    def create_widgets(self):
        # Main container frame
        main_frame = tk.Frame(self.root, bg="#E3F2FD", bd=2, relief=tk.RIDGE)
        main_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

        # Left side - Order form
        order_frame = tk.Frame(main_frame, bg="#E3F2FD", padx=10, pady=10)
        order_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Right side - Menu display
        menu_frame = tk.Frame(main_frame, bg="#E3F2FD", padx=10, pady=10)
        menu_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Order form elements
        tk.Label(order_frame, text="Create Your Order", font=("Arial", 16, "bold"),
                 bg="#E3F2FD", fg="#2B2E4A").pack(pady=5)

        # Customer info
        info_frame = tk.LabelFrame(order_frame, text="Customer Information", bg="#E3F2FD",
                                   fg="#2B2E4A", font=("Arial", 10, "bold"))
        info_frame.pack(fill=tk.X, pady=5)

        tk.Label(info_frame, text="Name:", bg="#E3F2FD").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.name_entry = tk.Entry(info_frame)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)

        tk.Label(info_frame, text="Phone:", bg="#E3F2FD").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.phone_entry = tk.Entry(info_frame)
        self.phone_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=2)

        # Order details
        order_details_frame = tk.LabelFrame(order_frame, text="Order Details", bg="#E3F2FD",
                                            fg="#2B2E4A", font=("Arial", 10, "bold"))
        order_details_frame.pack(fill=tk.X, pady=5)

        # Flavor selection
        tk.Label(order_details_frame, text="Flavor:", bg="#E3F2FD").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.flavor_var = tk.StringVar(value=list(self.menu_items.keys())[0])
        self.flavor_menu = ttk.Combobox(order_details_frame, textvariable=self.flavor_var,
                                        values=list(self.menu_items.keys()), state="readonly")
        self.flavor_menu.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=2)
        self.flavor_menu.current(0)

        # Scoops selection
        tk.Label(order_details_frame, text="Scoops:", bg="#E3F2FD").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.scoops_var = tk.IntVar(value=1)
        for i in range(3):
            tk.Radiobutton(order_details_frame, text=str(i + 1), variable=self.scoops_var,
                           value=i + 1, bg="#E3F2FD").grid(row=1, column=i + 1, padx=5, pady=2)

        # Container selection
        tk.Label(order_details_frame, text="Container:", bg="#E3F2FD").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.container_var = tk.StringVar(value="Cup")
        tk.Radiobutton(order_details_frame, text="Cup", variable=self.container_var,
                       value="Cup", bg="#E3F2FD").grid(row=2, column=1, padx=5, pady=2)
        tk.Radiobutton(order_details_frame, text="Cone", variable=self.container_var,
                       value="Cone", bg="#E3F2FD").grid(row=2, column=2, padx=5, pady=2)

        # Payment method
        tk.Label(order_details_frame, text="Payment:", bg="#E3F2FD").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.payment_var = tk.StringVar(value="Cash")
        self.payment_var.trace_add("write", lambda *args: self.toggle_card_entry())
        tk.Radiobutton(order_details_frame, text="Cash", variable=self.payment_var,
                       value="Cash", bg="#E3F2FD").grid(row=3, column=1, padx=5, pady=2)
        tk.Radiobutton(order_details_frame, text="Card", variable=self.payment_var,
                       value="Card", bg="#E3F2FD").grid(row=3, column=2, padx=5, pady=2)

        # Card number field (hidden by default)
        self.card_label = tk.Label(order_details_frame, text="Card Number:", bg="#E3F2FD")
        self.card_entry = tk.Entry(order_details_frame)

        # Delivery method
        tk.Label(order_details_frame, text="Delivery:", bg="#E3F2FD").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.delivery_var = tk.StringVar(value="Takeaway")
        tk.Radiobutton(order_details_frame, text="Takeaway", variable=self.delivery_var,
                       value="Takeaway", bg="#E3F2FD", command=self.toggle_address).grid(row=4, column=1, padx=5, pady=2)
        tk.Radiobutton(order_details_frame, text="Delivery", variable=self.delivery_var,
                       value="Delivery", bg="#E3F2FD", command=self.toggle_address).grid(row=4, column=2, padx=5, pady=2)

        # Address field (hidden by default)
        self.address_label = tk.Label(order_details_frame, text="Address:", bg="#E3F2FD")
        self.address_text = scrolledtext.ScrolledText(order_details_frame, height=3, width=30)

        # Order summary (Total will be shown here!)
        summary_frame = tk.LabelFrame(order_frame, text="Order Summary", bg="#E3F2FD",
                                      fg="#2B2E4A", font=("Arial", 10, "bold"))
        summary_frame.pack(fill=tk.BOTH, pady=5, expand=True)

        self.summary_text = tk.Text(summary_frame, height=8, bg="white", fg="#4B4453")
        self.summary_text.pack(fill=tk.BOTH, expand=True)

        # Place order button
        order_btn = tk.Button(order_frame, text="Place Order", command=self.place_order,
                              bg="#3F72AF", fg="white", font=("Arial", 12, "bold"))
        order_btn.pack(pady=10, ipadx=20)

        # Menu display
        tk.Label(menu_frame, text="Our Delicious Flavors", font=("Arial", 16, "bold"),
                 bg="#E3F2FD", fg="#2B2E4A").pack(pady=5)

        menu_display = tk.Frame(menu_frame, bg="#E3F2FD")
        menu_display.pack(fill=tk.BOTH, expand=True)

        # Add Flavor and Update Flavor buttons below "Our Delicious Flavors"
        btn_flavor_frame = tk.Frame(menu_frame, bg="#E3F2FD")
        btn_flavor_frame.pack(pady=2)
        add_flavor_btn = tk.Button(btn_flavor_frame, text="Add Flavor", command=self.add_flavor_popup,
                                   bg="#3F72AF", fg="white", font=("Arial", 10, "bold"))
        add_flavor_btn.pack(side=tk.LEFT, padx=4)
        update_flavor_btn = tk.Button(btn_flavor_frame, text="Update Flavor", command=self.update_flavor_popup,
                                      bg="#3F72AF", fg="white", font=("Arial", 10, "bold"))
        update_flavor_btn.pack(side=tk.LEFT, padx=4)

        # Create a canvas and scrollbar for the menu
        self.menu_display = menu_display
        self.create_menu_canvas()

        # Order history section
        history_frame = tk.LabelFrame(menu_frame, text="Order History", bg="#E3F2FD",
                                      fg="#2B2E4A", font=("Arial", 10, "bold"))
        history_frame.pack(fill=tk.BOTH, pady=5, expand=True)

        self.history_text = tk.Text(history_frame, height=8, bg="white", fg="#4B4453")
        self.history_text.pack(fill=tk.BOTH, expand=True)

        # Update order summary and total initially
        self.update_summary()

        # Bind changes to update summary and total
        self.flavor_var.trace_add("write", lambda *args: self.update_summary())
        self.scoops_var.trace_add("write", lambda *args: self.update_summary())
        self.container_var.trace_add("write", lambda *args: self.update_summary())
        self.payment_var.trace_add("write", lambda *args: self.update_summary())
        self.delivery_var.trace_add("write", lambda *args: self.update_summary())

        self.toggle_address()
        self.toggle_card_entry()

    def create_menu_canvas(self):
        # Destroy previous menu canvas if exists
        if hasattr(self, 'canvas'):
            self.canvas.destroy()
        if hasattr(self, 'scrollbar'):
            self.scrollbar.destroy()
        if hasattr(self, 'scrollable_frame'):
            self.scrollable_frame.destroy()

        self.canvas = tk.Canvas(self.menu_display, bg="#E3F2FD", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.menu_display, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#E3F2FD")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Display menu items with "fancy" styling
        for i, (flavor, price) in enumerate(self.menu_items.items()):
            item_frame = tk.Frame(self.scrollable_frame, bg="#E3F2FD", bd=1, relief=tk.RIDGE)
            item_frame.pack(fill=tk.X, pady=2, padx=5)
            if i % 2 == 0:
                item_frame.configure(bg="#E3F2FD")

            tk.Label(item_frame, text=flavor, font=("Arial", 11),
                     bg=item_frame["bg"], fg="#4B4453").pack(side=tk.LEFT, padx=10)
            tk.Label(item_frame, text=f"Rs.{price:.2f}", font=("Arial", 11, "bold"),
                     bg=item_frame["bg"], fg="#2B2E4A").pack(side=tk.RIGHT, padx=10)

    def add_flavor_popup(self):
        # Popup window for adding a new flavor and price
        popup = tk.Toplevel(self.root)
        popup.title("Add Flavor")
        popup.geometry("280x140")
        popup.grab_set()
        popup.update_idletasks()
        w = 280
        h = 140
        x = (popup.winfo_screenwidth() // 2) - (w // 2)
        y = (popup.winfo_screenheight() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        tk.Label(popup, text="Flavor Name:", font=("Arial", 10)).pack(pady=5)
        flavor_entry = tk.Entry(popup)
        flavor_entry.pack(pady=2)

        tk.Label(popup, text="Price (Rs):", font=("Arial", 10)).pack(pady=5)
        price_entry = tk.Entry(popup)
        price_entry.pack(pady=2)

        def add_flavor_action():
            flavor = flavor_entry.get().strip()
            price_str = price_entry.get().strip()
            if not flavor or not price_str:
                messagebox.showerror("Error", "Please enter both flavor and price.")
                return
            try:
                price = float(price_str)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid price.")
                return
            if flavor in self.menu_items:
                messagebox.showerror("Error", "This flavor already exists.")
                return
            self.menu_items[flavor] = price
            self.save_menu_to_file(self.menu_txt_file, self.menu_items)
            self.flavor_menu["values"] = list(self.menu_items.keys())
            self.create_menu_canvas()
            messagebox.showinfo("Success", f"Added {flavor} for Rs.{price:.2f}!")
            popup.destroy()

        tk.Button(popup, text="Add", command=add_flavor_action, bg="#3F72AF", fg="white", font=("Arial", 10, "bold")).pack(pady=8)

    def update_flavor_popup(self):
        # Popup window for updating an existing flavor's name or price
        popup = tk.Toplevel(self.root)
        popup.title("Update Flavor")
        popup.geometry("350x200")
        popup.grab_set()
        popup.update_idletasks()
        w = 350
        h = 200
        x = (popup.winfo_screenwidth() // 2) - (w // 2)
        y = (popup.winfo_screenheight() // 2) - (h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")
        tk.Label(popup, text="Select Flavor to Update:", font=("Arial", 10)).pack(pady=5)
        selected_flavor_var = tk.StringVar(value=list(self.menu_items.keys())[0])
        flavor_list = ttk.Combobox(popup, textvariable=selected_flavor_var, values=list(self.menu_items.keys()), state="readonly")
        flavor_list.pack(pady=2)

        tk.Label(popup, text="New Name (optional):", font=("Arial", 10)).pack(pady=5)
        new_name_entry = tk.Entry(popup)
        new_name_entry.pack(pady=2)

        tk.Label(popup, text="New Price (optional):", font=("Arial", 10)).pack(pady=5)
        new_price_entry = tk.Entry(popup)
        new_price_entry.pack(pady=2)

        def update_flavor_action():
            old_flavor = selected_flavor_var.get()
            new_name = new_name_entry.get().strip()
            new_price_str = new_price_entry.get().strip()
            if not old_flavor:
                messagebox.showerror("Error", "Please select a flavor to update.")
                return
            # New name blank means keep same name
            if not new_name:
                new_name = old_flavor
            # New price blank means keep same price
            if not new_price_str:
                new_price = self.menu_items[old_flavor]
            else:
                try:
                    new_price = float(new_price_str)
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid price.")
                    return
            # If name changed and new name already exists
            if new_name != old_flavor and new_name in self.menu_items:
                messagebox.showerror("Error", "This new flavor name already exists.")
                return
            # Update menu dict
            if new_name != old_flavor:
                self.menu_items[new_name] = self.menu_items.pop(old_flavor)
            self.menu_items[new_name] = new_price
            self.save_menu_to_file(self.menu_txt_file, self.menu_items)
            self.flavor_menu["values"] = list(self.menu_items.keys())
            self.flavor_var.set(list(self.menu_items.keys())[0])
            self.create_menu_canvas()
            messagebox.showinfo("Success", f"Flavor updated: {old_flavor} -> {new_name}, Price: Rs.{new_price:.2f}")
            popup.destroy()

        tk.Button(popup, text="Update", command=update_flavor_action, bg="#3F72AF", fg="white", font=("Arial", 10, "bold")).pack(pady=8)

    def toggle_card_entry(self):
        # Show/hide the card number field based on payment method
        if self.payment_var.get() == "Card":
            self.card_label.grid(row=5, column=0, sticky=tk.W, padx=5, pady=2)
            self.card_entry.grid(row=5, column=1, columnspan=2, sticky=tk.EW, padx=5, pady=2)
        else:
            self.card_label.grid_remove()
            self.card_entry.grid_remove()
        self.update_summary()

    def update_total(self):
        flavor = self.flavor_var.get()
        scoops = self.scoops_var.get()
        container = self.container_var.get()
        try:
            total = self.calculate_icecream_price(
                flavor, scoops, self.menu_items, container, self.container_prices
            )
            return total
        except Exception:
            return 0.0

    def toggle_address(self):
        if self.delivery_var.get() == "Delivery":
            self.address_label.grid(row=6, column=0, sticky=tk.NW, padx=5, pady=2)
            self.address_text.grid(row=6, column=1, columnspan=3, sticky=tk.EW, padx=5, pady=2)
        else:
            self.address_label.grid_remove()
            self.address_text.grid_remove()
        self.update_summary()

    def update_summary(self):
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)

        name = self.name_entry.get() or "Customer"
        flavor = self.flavor_var.get()
        scoops = self.scoops_var.get()
        container = self.container_var.get()
        payment = self.payment_var.get()
        delivery = self.delivery_var.get()
        total = self.update_total()

        # Only use ASCII in summary for PDF compatibility
        summary = f"Order Summary for {name}:\n\n"
        summary += f"- {scoops} scoop(s) of {flavor} in a {container}\n"
        summary += f"- Payment: {payment}\n"
        if payment == "Card":
            card_number = self.card_entry.get()
            if card_number:
                summary += f"- Card Number: ****{card_number[-4:]}\n"
            else:
                summary += f"- Card Number: [Please enter card number]\n"
        summary += f"- Delivery: {delivery}\n"
        summary += f"- Total: Rs.{total:.2f}\n"

        if delivery == "Delivery":
            address = self.address_text.get(1.0, tk.END).strip()
            if address:
                summary += f"- Delivery address: {address}\n"
            else:
                summary += "- Delivery address: [Please enter address]\n"

        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state=tk.DISABLED)

    def generate_pdf_receipt(self, order):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # Restaurant Name
        pdf.cell(200, 10, txt="Velvet Cone", ln=True, align='C')
        pdf.ln(5)

        # Customer Name and Order ID
        pdf.cell(200, 10, txt=f"Name: {order['customer_name']}", ln=True)
        pdf.cell(200, 10, txt=f"Order ID: {order['order_id']}", ln=True)
        pdf.cell(200, 10, txt=f"Time: {order['timestamp']}", ln=True)
        pdf.ln(5)

        # Order Summary
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, "Order Summary:", ln=True)
        pdf.set_font("Arial", size=12)

        # Use only ASCII-safe summary
        safe_summary = order['summary'].encode('ascii', 'replace').decode('ascii')
        pdf.multi_cell(0, 10, safe_summary)
        pdf.ln(5)

        # Grand Total
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(200, 10, txt=f"Grand Total: Rs. {order['total']:.2f}", ln=True)

        filename = f"{order['order_id']}_receipt.pdf"
        pdf.output(filename)
        return filename

    def load_all_orders(self):
        """Load all orders from text file into self.order_history."""
        self.order_history = []
        if os.path.exists(self.orders_file):
            with open(self.orders_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            order_dict = ast.literal_eval(line.strip())
                            self.order_history.append(order_dict)
                        except Exception:
                            continue

    def save_order_to_file(self, order):
        """Append the new order to the text file."""
        try:
            with open(self.orders_file, "a", encoding="utf-8") as f:
                f.write(str(order) + "\n")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save order to file: {e}")

    def place_order(self):
        if not self.name_entry.get():
            messagebox.showerror("Error", "Please enter your name")
            return

        if not self.phone_entry.get():
            messagebox.showerror("Error", "Please enter your phone number")
            return
        if any(char.isdigit() for char in self.name_entry.get()):
            messagebox.showerror("Error", "Name should not contain numbers.")
            return

        if any(char.isalpha() for char in self.phone_entry.get()):
            messagebox.showerror("Error", "Phone number should not contain letters.")
            return

        # Card number validation
        if self.payment_var.get() == "Card":
            card_number = self.card_entry.get()
            if not card_number or card_number.strip() == "":
                messagebox.showerror("Error", "Please enter your card number")
                return

        if self.delivery_var.get() == "Delivery" and not self.address_text.get(1.0, tk.END).strip():
            messagebox.showerror("Error", "Please enter delivery address")
            return

        flavor = self.flavor_var.get()
        scoops = self.scoops_var.get()
        container = self.container_var.get()
        total = self.calculate_icecream_price(
            flavor, scoops, self.menu_items, container, self.container_prices
        )

        name = self.name_entry.get()
        phone = self.phone_entry.get()
        payment = self.payment_var.get()
        delivery = self.delivery_var.get()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # ASCII-safe summary for PDF
        summary = f"Order Summary for {name}:\n\n"
        summary += f"- {scoops} scoop(s) of {flavor} in a {container}\n"
        summary += f"- Payment: {payment}\n"
        if payment == "Card":
            card_number = self.card_entry.get()
            if card_number:
                summary += f"- Card Number: ****{card_number[-4:]}\n"
            else:
                summary += f"- Card Number: [Please enter card number]\n"
        summary += f"- Delivery: {delivery}\n"
        summary += f"- Total: Rs.{total:.2f}\n"

        if delivery == "Delivery":
            address = self.address_text.get(1.0, tk.END).strip()
            if address:
                summary += f"- Delivery address: {address}\n"
            else:
                summary += "- Delivery address: [Please enter address]\n"

        order = {
            "order_id": random.randint(1000, 9999),
            "customer_name": name,
            "phone": phone,
            "flavor": flavor,
            "scoops": scoops,
            "container": container,
            "payment": payment,
            "delivery": delivery,
            "total": total,
            "timestamp": timestamp,
            "summary": summary
        }

        if order["delivery"] == "Delivery":
            order["address"] = self.address_text.get(1.0, tk.END).strip()
        if order["payment"] == "Card":
            order["card_number"] = self.card_entry.get()

        self.order_history.append(order)
        self.save_order_to_file(order)
        self.update_history()

        # Generate PDF receipt
        pdf_filename = self.generate_pdf_receipt(order)

        # Show confirmation with "Download Receipt" option
        self.show_receipt_popup(order, pdf_filename)

        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.flavor_var.set(list(self.menu_items.keys())[0])
        self.scoops_var.set(1)
        self.container_var.set("Cup")
        self.payment_var.set("Cash")
        self.delivery_var.set("Takeaway")
        self.address_text.delete(1.0, tk.END)
        self.card_entry.delete(0, tk.END)
        self.toggle_address()
        self.toggle_card_entry()
        self.update_summary()

    def show_receipt_popup(self, order, pdf_filename):
        def download_receipt():
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                initialfile=pdf_filename,
                filetypes=[("PDF files", "*.pdf")]
            )
            if file_path:
                shutil.copy(pdf_filename, file_path)
                messagebox.showinfo("Receipt Saved", f"Receipt saved to: {file_path}")

        popup = tk.Toplevel(self.root)
        popup.title("Order Placed")
        popup.geometry("350x180")
        popup.grab_set()  # Make modal
        self.root.update_idletasks()
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()
        popup_w = 350
        popup_h = 180
        x = root_x + (root_w // 2) - (popup_w // 2)
        y = root_y + (root_h // 2) - (popup_h // 2)
        popup.geometry(f"{popup_w}x{popup_h}+{x}+{y}")

        tk.Label(popup, text=f"Order #{order['order_id']} has been placed!",
                 font=("Arial", 12, "bold")).pack(pady=10)
        tk.Label(popup, text=f"Thank you, {order['customer_name']}!", font=("Arial", 11)).pack()
        tk.Label(popup, text=f"Total: Rs.{order['total']:.2f}", font=("Arial", 11)).pack(pady=5)
        download_btn = tk.Button(popup, text="Download Receipt", command=download_receipt,
                                 bg="#3F72AF", fg="white", font=("Arial", 11, "bold"))
        download_btn.pack(pady=10)
        tk.Button(popup, text="Close", command=popup.destroy, font=("Arial", 10)).pack()
        
    def update_history(self):
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)

        if not self.order_history:
            self.history_text.insert(tk.END, "No orders placed yet.")
            self.history_text.config(state=tk.DISABLED)
            return

        for order in self.order_history[-5:]:
            self.history_text.insert(tk.END,
                                    f"Order #{order['order_id']} - {order['timestamp']}\n"
                                    f"{order['customer_name']} ({order['phone']}): {order['scoops']}x {order['flavor']}\n"
                                    f"({order['container']}, {order['payment']}, {order['delivery']}, Total: Rs.{order['total']:.2f})\n\n")

        self.history_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = IceCreamShopApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
                                   

