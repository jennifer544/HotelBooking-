import mysql.connector
from tabulate import tabulate
from datetime import datetime, timedelta


# Connect to MySQL Database
def connect_to_database():
    try:
        return mysql.connector.connect(
            host='localhost',
            user='root',
            password='Jennifer@21',
            database='HotelManagement'
        )
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


databaseobj = connect_to_database()
cursor = databaseobj.cursor() if databaseobj else None


# Create tables with improved error handling
def create_tables():
    if cursor is None:
        print("Database connection not established.")
        return

    try:
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            category_name VARCHAR(50) PRIMARY KEY,
            description VARCHAR(255)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS rooms (
            room_id INT AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(50) NOT NULL,
            room_number INT NOT NULL,
            rate DECIMAL(10, 2) NOT NULL,
            FOREIGN KEY (category) REFERENCES categories(category_name)
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id VARCHAR(7) PRIMARY KEY,
            customer_name VARCHAR(255) NOT NULL,
            room_id INT NOT NULL,
            date_of_booking DATE NOT NULL,
            date_of_occupancy DATE NOT NULL,
            number_of_days INT NOT NULL,
            advance_received DECIMAL(10, 2),
            FOREIGN KEY (room_id) REFERENCES rooms(room_id)
        )
        ''')

        databaseobj.commit()
        print("Tables created successfully.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


create_tables()

# Hardcoded admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'
MAX_ATTEMPTS = 3


# Function to handle admin login
def admin_login():
    if cursor is None:
        print("Database connection not established.")
        return

    attempts = 0
    while attempts < MAX_ATTEMPTS:
        username = input("Enter your username: ")
        password = input("Enter your password: ")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            print("Admin login successful!")
            admin_panel()
            return
        else:
            attempts += 1
            print(f"Incorrect username or password. Attempt {attempts} of {MAX_ATTEMPTS}.")

    print("Maximum number of attempts reached. Please try again later.")


# Admin panel functionalities
def admin_panel():
    while True:
        print("\nAdmin Panel")
        print("1.View All Bookings")
        print("2. Add Room Category")
        print("3. Add Room")
        print("4. List Occupied Rooms")
        print("5. Display Rooms by Rate")
        print("6. Update Room Status")
        print("7. Store and Display Records")
        print("8. Exit")

        choice = input("Choose an option: ")
        if choice == '1':
            list_all_bookings()
        elif choice == '2':
            add_category()
        elif choice == '3':
            add_room()
        elif choice == '4':
            list_occupied_rooms()
        elif choice == '5':
            display_rooms_by_rate()
        elif choice == '6':
            update_room_status()
        elif choice == '7':
            store_and_display_records()
        elif choice == '8':
            break
        else:
            print("Invalid choice. Please try again.")


# Add a new room category
def add_category():
    if cursor is None:
        print("Database connection not established.")
        return

    while True:
        try:
            # Retrieve and list existing categories
            cursor.execute("SELECT category_name FROM categories")
            categories = cursor.fetchall()
            print("\nExisting categories:")
            for category in categories:
                print(f"- {category[0]}")

1            # Get category name and description from user
            category_name = input("Enter room category (e.g., Single, Double, Suite, Convention halls, Ball rooms): ")

            # Check if category already exists
            cursor.execute("SELECT category_name FROM categories WHERE category_name = %s", (category_name,))
            if cursor.fetchone():
                print(f"Category '{category_name}' already exists.")
                continue

            description = input("Enter a brief description: ")

            # Insert new category into the database
            insert_query = "INSERT INTO categories (category_name, description) VALUES (%s, %s)"
            cursor.execute(insert_query, (category_name, description))
            databaseobj.commit()
            print("Category added successfully!")

            # Option to add another category or return to admin panel
            choice = input("Do you want to add another category? (y/n): ").strip().lower()
            if choice != 'y':
                break
        except mysql.connector.Error as err:
            print(f"Error: {err}")


# Add a new room
def add_room():
    if cursor is None:
        print("Database connection not established.")
        return

    while True:
        try:
            category = input("Enter room category: ")
            room_number = int(input("Enter room number: "))
            rate = float(input("Enter rate per day: "))

            insert_query = "INSERT INTO rooms (category, room_number, rate) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (category, room_number, rate))
            databaseobj.commit()
            print("Room added successfully!")
            break
        except mysql.connector.Error as err:
            print(f"Error: {err}")


# List all rooms which are occupied for next two days
def list_occupied_rooms():
    if cursor is None:
        print("Database connection not established.")
        return

    try:
        today = datetime.today().date()  # Correct way to get today's date
        two_days_later = today + timedelta(days=2)  # Calculate two days later

        query = '''
            SELECT r.room_id, r.category, b.date_of_occupancy, b.customer_name
            FROM rooms r
            JOIN bookings b ON r.room_id = b.room_id
            WHERE b.date_of_occupancy BETWEEN %s AND %s
        '''
        cursor.execute(query, (today, two_days_later))
        query_result = cursor.fetchall()

        if query_result:
            print(tabulate(query_result, headers=["Room ID", "Category", "Date of Occupancy", "Customer Name"]))
        else:
            print("No rooms are occupied in the next two days.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")
# Display rooms by rate
def display_rooms_by_rate():
    if cursor is None:
        print("Database connection not established.")
        return

    try:
        cursor.execute("SELECT * FROM rooms ORDER BY rate")
        result = cursor.fetchall()
        if result:
            print(tabulate(result, headers=["Room ID", "Category", "Room Number", "Rate","Status"]))
        else:
            print("No rooms found.")
    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Update room status to unoccupied when the customer leaves
def update_room_status():
    if cursor is None:
        print("Database connection not established.")
        return

    try:
        room_id = int(input("Enter room ID to update: "))

        # Fetch the current status of the room
        cursor.execute("SELECT status FROM rooms WHERE room_id=%s", (room_id,))
        result = cursor.fetchone()

        if result is None:
            print("Room not found.")
            return

        current_status = result[0]

        # Toggle the room status
        new_status = 'occupied' if current_status == 'unoccupied' else 'unoccupied'

        # Update the room status in the database
        update_query = "UPDATE rooms SET status = %s WHERE room_id = %s"
        cursor.execute(update_query, (new_status, room_id))
        databaseobj.commit()

        print(f"Room status updated to {new_status}.")

        # Fetch and display the updated room details
        cursor.execute("SELECT room_id, category, room_number, rate, status FROM rooms WHERE room_id = %s", (room_id,))
        updated_room = cursor.fetchone()

        if updated_room:
            print("\nUpdated Room Details:")
            print(tabulate([updated_room], headers=["Room ID", "Category", "Room Number", "Rate", "Status"]))
        else:
            print("Error fetching updated room details.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    except ValueError:
        print("Invalid input. Please enter a valid room ID.")


# Store all records in file and display from file
def store_and_display_records():
    if cursor is None:
        print("Database connection not established.")
        return

    try:
        cursor.execute("SELECT * FROM rooms")
        rooms = cursor.fetchall()

        with open('rooms.txt', 'w') as file:
            for room in rooms:
                file.write(f"{room}\n")

        with open('rooms.txt', 'r') as file:
            print("\nRecords from file:")
            for line in file:
                print(line.strip())
    except mysql.connector.Error as err:
        print(f"Error: {err}")


def list_all_bookings():
    if cursor is None:
        print("Database connection not established.")
        return

    try:
        # Fetch all records from the bookings table
        cursor.execute('''
            SELECT booking_id, customer_name, room_id, date_of_booking, date_of_occupancy, number_of_days, advance_received 
            FROM bookings
        ''')
        bookings = cursor.fetchall()

        if bookings:
            # Display the bookings using tabulate for better formatting
            print("\nAll Bookings:")
            print(tabulate(bookings,
                           headers=["Booking ID", "Customer Name", "Room ID", "Date of Booking", "Date of Occupancy",
                                    "Number of Days", "Advance Received"]))
        else:
            print("No bookings found.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")


# Main function to start the program
def main():
    while True:
        print("\nWelcome to the Hotel Management System")
        print("1. Admin Login")
        print("2. Exit")

        choice = input("Choose an option: ")

        if choice == '1':
            admin_login()
        elif choice == '2':
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
