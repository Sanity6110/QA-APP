#!/usr/bin/env python3
import mysql.connector
from mysql.connector import errorcode

# Change these as needed
DB_CONFIG = {
    'user':     'root',
    'password': 'WjhQN70VBMSvmdrVkZl0@',
    'host':     '127.0.0.1',
    'port':     3306,
    'ssl_disabled': True
}

DB_NAME = 'PrintersCMDB'

TABLES = {}
TABLES['printers'] = (
    "CREATE TABLE `printers` ("
    "  `id` INT NOT NULL AUTO_INCREMENT,"
    "  `name` VARCHAR(100) NOT NULL,"
    "  `model` VARCHAR(100) NOT NULL,"
    "  `location` VARCHAR(100),"
    "  `ip_address` VARCHAR(45),"
    "  `status` ENUM('Online','Offline','Unknown') DEFAULT 'Unknown',"
    "  PRIMARY KEY (`id`)"
    ") ENGINE=InnoDB"
)

DUMMY_PRINTERS = [
    ('Printer1', 'HP LaserJet Pro M404dn',  'Floor 1 – Room A', '192.168.1.100', 'Online'),
    ('Printer2', 'Canon imageCLASS MF743Cdw','Floor 2 – Room B', '192.168.1.101', 'Offline'),
    ('Printer3', 'Epson EcoTank ET-4760',   'Floor 3 – Room C', '192.168.1.102', 'Online'),
]

def main():
    # 1) Connect to MySQL server
    try:
        cnx = mysql.connector.connect(**DB_CONFIG)
        cursor = cnx.cursor()
        print("Connected to MySQL server.")
    except mysql.connector.Error as err:
        print(f"ERROR: {err}")
        return

    # 2) Create database
    try:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` DEFAULT CHARACTER SET 'utf8mb4'")
        print(f"Database `{DB_NAME}` ensured.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        cursor.close()
        cnx.close()
        return

    # 3) Select the database
    cnx.database = DB_NAME

    # 4) Create tables
    for table_name, ddl in TABLES.items():
        try:
            print(f"Creating table `{table_name}`...", end='')
            cursor.execute(ddl)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(f"failed: {err}")

    # 5) Insert dummy data
    insert_stmt = (
        "INSERT INTO printers "
        "(name, model, location, ip_address, status) "
        "VALUES (%s, %s, %s, %s, %s)"
    )
    try:
        cursor.executemany(insert_stmt, DUMMY_PRINTERS)
        cnx.commit()
        print(f"{cursor.rowcount} dummy records inserted into `printers`.")
    except mysql.connector.Error as err:
        print(f"Failed inserting dummy data: {err}")
        cnx.rollback()

    # 6) Cleanup
    cursor.close()
    cnx.close()
    print("Done.")

if __name__ == "__main__":
    main()
 