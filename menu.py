flavors = {
    "Vanilla Bean": 150,
    "Chocolate Fudge": 170,
    "Strawberry Swirl": 160,
    "Mint Chocolate Chip": 180,
    "Salted Caramel": 190,
     "Cookies and Cream": 175,
    "Pistachio Delight": 200,
    "Coffee Espresso": 180,
    "Mango Sorbet": 165,
    "Butter Pecan": 190,
    "Lemon Cheesecake": 185,
    "Black Cherry": 170,
    "Peanut Butter Cup": 195,
    "Coconut Dream": 175,
    "Raspberry Ripple": 180,
    "Tiramisu": 195,
    "Honeycomb Crunch": 185,
    "Blueberry Muffin": 170,
    "Matcha Green Tea": 200,
    "Birthday Cake": 190
}

with open("menu.txt", "w") as file:
    for flavor, price in flavors.items():
        file.write(f"{flavor} - {price}\n")

print("menu.txt created!")


