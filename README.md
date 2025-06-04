# Velvet-cone-ordering
A simple food ordering system with menu file handling and order history storage.

GUI LAYOUT EXPLANATION:
The Tkinter-based interface features input sections for user details and order customization, organized via grid() layout. 
Key components include:
Entry fields (name, phone) and radio buttons (delivery/pickup)
Dynamic address fields that toggle based on delivery selection
Comboboxes (flavour/container/toppings) and quantity spinbox
The system calculates totals in real-time  and validates all inputs upon submission. After order confirmation, it:
Generates a PDF receipt using ReportLab
Displays a popup with order summary and options to quit/restart
This streamlined flow ensures data accuracy while maintaining user-friendly operation from selection to receipt.
The Add button allows the user to input a new flavour name and price, which is appended to the menu file
The Update button enables the modification of existing flavour prices by selecting the flavour from a dropdown and updating its cost, ensuring changes are reflected in the file immediately.

LIST OF FEATURES IMPLEMENTED:
User friendly Tkinter GUI with grid layout.
Order type selection (delivery/pickup)
Customizable order option (flavour, container, scoops)
Real-time price calculation
Input validation for mandatory fields
PDF receipt generation
Order confirmation popup
Add new menu items (flavours and prices) with "Add" button
Update existing flavour prices with "Update" button
