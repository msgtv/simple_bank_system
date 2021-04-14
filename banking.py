from random import randint
import sqlite3


def create_table():
    global cur
    cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0 NOT NULL);")


class Bank:
    data = None
    card_num = 'NULL'
    pin_code = None
    balance = None

    def __init__(self):
        self.data = dict()

    def create_acc(self):
        global cur
        global conn
        while self.card_num == 'NULL' and cur.fetchone() is None or self.card_num == str(cur.fetchone()).strip("()',"):
            self.card_num = self.num_card()
        self.pin_code = self.pin()
        self.insert_data()
        cur.execute(f"SELECT number FROM card WHERE number = {self.card_num}")
        conn.commit()

    def num_card(self):
        step1 = list('400000' + ''.join([str(randint(0, 9)) for _ in range(9)]))
        checksum = self.luhn_algorithm('create', step1)
        step1.append(str(checksum))
        num = ''.join(step1)
        return ''.join(num)

    @staticmethod
    def pin():
        return ''.join(str(randint(0, 9)) for _ in range(4))

    def authentication(self):
        num = input("\nEnter your card number:\n")
        pin = input("Enter your PIN:\n")
        if self.check(num, pin):
            print("\nYou have successfully logged in!\n")
            cur.execute(f"SELECT number FROM card WHERE number = {num}")
            self.card_num = cur.fetchone()[0]
            self.balance = self.balance_viewer()
            self.private_page()
        else:
            print("\nWrong card number or PIN!\n")

    @staticmethod
    def check(num, pin):
        global cur
        cur.execute(f"SELECT pin FROM card WHERE number = {num};")
        pin_bd = str(cur.fetchone()).strip("()',")
        if pin_bd and pin_bd == pin:
            return True
        else:
            return False

    def private_page(self):
        while True:
            print("1. Balance")
            print("2. Add income")
            print("3. Do transfer")
            print("4. Close account")
            print("5. Log out")
            print("0. Exit")
            choice_list = ('1', '2', '3', '4', '5', '0')
            while True:
                choice = input()
                if choice in choice_list:
                    break
            if choice == '1':
                print(f"\nBalance: {self.balance}\n")
            elif choice == '2':
                self.add_income()
            elif choice == '3':
                self.do_transfer()
            elif choice == '4':
                self.delete_acc()
                break
            elif choice == '5':
                print("\nYou have successfully logged out!\n")
                break
            elif choice == '0':
                print("\nBye!")
                conn.commit()
                conn.close()
                exit()

    def balance_viewer(self):
        global cur
        cur.execute(f"SELECT balance FROM card WHERE number = {self.card_num};")
        balance = cur.fetchone()[0]
        return balance

    def add_income(self):
        global cur
        global conn
        income = ''
        while not income.isdigit() or income.startswith('-'):
            income = input("\nEnter income:\n")
        print()
        self.balance = int(self.balance_viewer()) + int(income)
        cur.execute(f"UPDATE card SET balance = {self.balance} WHERE number = {self.card_num};")
        conn.commit()

    def delete_acc(self):
        global cur
        global conn
        cur.execute(f"DELETE FROM card WHERE number = {self.card_num}")
        print("\nThe account has been closed!\n")
        conn.commit()

    def do_transfer(self):
        global cur
        global conn
        print("\nTransfer")
        num = ''
        while not num.isdigit() or (num.startswith('-') and len(num) != 16):
            num = input("Enter card number:\n")
        checking_num = list(num)
        checksum = checking_num.pop()
        if self.luhn_algorithm('check', checking_num, checksum):
            cur.execute(f"SELECT number FROM card WHERE number = {num};")
            output = cur.fetchone()
            print("####  output is None:", output is None)
            if output is None:
                print("Such a card does not exist.\n")
            elif output[0] == self.card_num:
                print("You can't transfer money to the same account!\n")
            else:
                self.transfer_money(num)
                conn.commit()

        else:
            print("Probably you made a mistake in the card number. Please try again!\n")

    def transfer_money(self, num_receiver):
        money = ''
        while not money or not money.isdigit() and money.startswith('-'):
            money = input("Enter how much money you want to transfer:\n")
        money = int(money)
        if money > int(self.balance):
            print("Not enough money!")
        else:
            cur.execute(f"SELECT balance FROM card WHERE number = {num_receiver}")
            balance_receiver = cur.fetchone()[0] + money
            cur.execute(f"SELECT balance FROM card WHERE number = {self.card_num}")
            self.balance -= money
            cur.execute(f"UPDATE card SET balance = {balance_receiver} WHERE number = {num_receiver}")
            cur.execute(f"UPDATE card SET balance = {self.balance} WHERE number = {self.card_num}")
            print("Success!\n")

    @staticmethod
    def luhn_algorithm(choice, num, card_checksum=None):
        step2 = []
        step3 = []
        for i in range(len(num)):
            if not i % 2:
                step2.append(int(num[i]) * 2)
            else:
                step2.append(int(num[i]))
        for i in step2:
            if i > 9:
                step3.append(i - 9)
            else:
                step3.append(i)
        x = sum(step3) % 10
        checksum = (10 - x) % 10
        if choice == 'create':
            return checksum
        elif choice == 'check':
            if int(card_checksum) == checksum:
                return True
            else:
                return False

    def work(self):
        global conn, cur
        while True:
            print("1. Create an account")
            print("2. Log into account")
            print("0. Exit")
            choice_list = ['1', '2', '0']
            while True:
                choice = input()
                if choice in choice_list:
                    break
            if choice == '1':
                self.create_acc()
            elif choice == '2':
                self.authentication()
            elif choice == '0':
                print("\nBye!")
                conn.commit()
                conn.close()
                exit()

    def insert_data(self):
        global cur
        cur.execute(f"INSERT INTO card (number, pin) VALUES ({self.card_num}, {self.pin_code});")
        print("\nYour card has been created")
        print(f"Your card number:\n{self.card_num}")
        print(f"Your card PIN:\n{self.pin_code}\n")


conn = sqlite3.connect('card.s3db')
cur = conn.cursor()
create_table()

bank = Bank()
bank.work()
