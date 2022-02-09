import random
from random import randint
import sqlite3

main_menu_list = ['1. Create an account', '2. Log into account', '0. Exit']
user_menu_list = ['1. Balance', '2. Add income', '3. Do transfer', '4. Close account', '5. Log out', '0. Exit']
option_list = ['0', '1', '2']
user_option_list = ['0', '1', '2', '3', '4', '5']
accounts_list = []
current_user = None
cur = None


def sum_digits(digit):
    if digit < 10:
        return digit
    else:
        sum_ = (digit % 10) + (digit // 10)
        return sum_


def validate(cc_num):
    cc_num = str(cc_num)
    cc_num = cc_num[::-1]
    cc_num = [int(x) for x in cc_num]
    doubled_second_digit_list = list()
    digits = list(enumerate(cc_num, start=1))
    for index, digit in digits:
        if index % 2 == 0:
            doubled_second_digit_list.append(digit * 2)
        else:
            doubled_second_digit_list.append(digit)

    doubled_second_digit_list = [sum_digits(x) for x in doubled_second_digit_list]
    sum_of_digits = sum(doubled_second_digit_list)
    return sum_of_digits % 10 == 0


def database_connection():
    conn = sqlite3.connect('card.s3db')
    global cur
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS card ('
                'id INTEGER,'
                'number TEXT,'
                'pin TEXT,'
                'balance INTEGER DEFAULT 0,'
                'isLogged BOOLEAN'
                ');')
    conn.commit()


def load_accounts():
    global accounts_list
    accounts_list = []
    conn = sqlite3.connect('card.s3db')
    global cur
    cur = conn.cursor()
    cur.execute('SELECT * FROM card;')
    for i in cur.fetchall():
        str(i).split(', ')
        accounts_list.append(CreditCardDB(i[0], int(i[1]), i[2], bool(i[4]), i[3]))


def generate_card_number():
    card_number = '4000000'
    sum_ = 0
    start_index = 'even'
    for x in range(8):
        card_number += str(randint(0, 9))

    for char in card_number:
        x = int(char)
        if start_index == 'even':
            start_index = 'odd'
            x *= 2
            if x > 9:
                x -= 9
        else:
            if x > 9:
                x -= 9
            start_index = 'even'
        sum_ += x

    if sum_ % 10 == 0:
        card_number += '0'
    else:
        check_sum = 10 - (sum_ % 10)
        card_number += str(check_sum)
    return int(card_number)


def generate_card_pin():
    pin_number = ''
    pin_number += str(randint(1, 9))
    for x in range(3):
        pin_number += str(randint(0, 9))
    return pin_number


class CreditCard:
    def __init__(self):
        self.card_number = generate_card_number()
        self.pin_number = generate_card_pin()
        self.logged_in = False
        self.balance = 0


class CreditCardDB:
    def __init__(self, id_, card_number, pin_number, logged_in, balance):
        self.id_ = id_
        self.card_number = card_number
        self.pin_number = pin_number
        self.logged_in = logged_in
        self.balance = balance

    def log_out(self):
        self.logged_in = False

    def log_in(self, card_pin):
        if card_pin == self.pin_number:
            self.logged_in = True
            return True
        else:
            return False

    def check_balance(self):
        print('Balance:', self.balance)

    def add_to_balance(self, income):
        self.balance += income


def is_anyone_logged_in(user_list):
    for user in user_list:
        if user.logged_in:
            global current_user
            current_user = accounts_list.index(user)
            return True
    return False


def create_card():
    new_account = CreditCard()
    conn = sqlite3.connect('card.s3db')
    global cur
    cur = conn.cursor()
    sql = "INSERT INTO card (id, number, pin, isLogged, balance) VALUES (%s, %s, %s, %s, %s)" % (
        (random.randint(1, 9999), new_account.card_number, str(new_account.pin_number), False, new_account.balance))
    cur.execute(sql)
    conn.commit()
    load_accounts()
    print('Your card has been created', 'Your card number:', accounts_list[-1].card_number,
          'Your card PIN:', accounts_list[-1].pin_number, sep='\n')


def log_in_option():
    card_nbr, pin_nbr, verification_success = None, None, None
    load_accounts()
    print('Enter your card number:')
    card_nbr = int(input())
    print('Enter your PIN:')
    pin_nbr = input()

    for user in accounts_list:
        if user.card_number == card_nbr:
            if user.log_in(pin_nbr):
                verification_success = True
                break
            else:
                verification_success = False
        else:
            verification_success = False

    if verification_success:
        print('You have successfully logged in!')
    else:
        print('Wrong card number or PIN!')


def check_balance_option():
    accounts_list[current_user].check_balance()


def log_out_option():
    accounts_list[current_user].log_out()


def add_funds():
    print('Enter income:')
    income = int(input())
    accounts_list[current_user].add_to_balance(income)
    conn = sqlite3.connect('card.s3db')
    global cur
    cur = conn.cursor()
    sql = "UPDATE card SET balance = %s WHERE number = %s" % (
        accounts_list[current_user].balance, accounts_list[current_user].card_number)
    cur.execute(sql)
    conn.commit()
    print('Income was added!')


def close_account():
    global current_user, cur
    conn = sqlite3.connect('card.s3db')
    cur = conn.cursor()
    sql = "DELETE FROM card WHERE id = %s" % accounts_list[current_user].id_
    cur.execute(sql)
    conn.commit()
    accounts_list.remove(accounts_list[current_user])
    current_user = None
    print('This account has been closed!')


def transfer_funds_init():
    print('Transfer\nEnter card number:')
    card_num = int(input())
    if validate(card_num):
        card_num_exists = False
        index = None
        for i in accounts_list:
            if i.card_number == card_num:
                card_num_exists = True
                index = accounts_list.index(i)
                break
        if card_num_exists:
            transfer_funds(card_num, index)
        else:
            print('Such a card does not exist.')
    else:
        print("Probably you made a mistake in the card number. Please try again!")


def transfer_funds(destination, destination_index):
    global cur
    print('Enter how much money you want to transfer:')
    amount = int(input())

    if accounts_list[current_user].balance < amount:
        print('Not enough money!')
    else:
        accounts_list[current_user].balance -= amount
        conn = sqlite3.connect('card.s3db')
        cur = conn.cursor()
        sql = "UPDATE card SET balance = %s WHERE id = %s" % (accounts_list[current_user].balance, accounts_list[current_user].id_)
        cur.execute(sql)
        accounts_list[destination_index].balance += amount
        sql = "UPDATE card SET balance = %s WHERE number = %s" % (accounts_list[destination_index].balance, destination)
        cur.execute(sql)
        conn.commit()
        print('Success!')


def menu_viewer():
    while True:
        if not is_anyone_logged_in(accounts_list):
            print("\n".join(main_menu_list))
            user_choice = input()
            if user_choice not in option_list:
                continue
            else:
                if user_choice == '0':
                    print('Bye!')
                    break
                elif user_choice == '1':
                    create_card()
                else:
                    log_in_option()
        else:
            print("\n".join(user_menu_list))
            user_choice = input()
            if user_choice not in user_option_list:
                continue
            else:
                if user_choice == '0':
                    print('Bye')
                    break
                elif user_choice == '1':
                    check_balance_option()
                elif user_choice == '5':
                    log_out_option()
                    global current_user
                    current_user = None
                elif user_choice == '2':
                    add_funds()
                elif user_choice == '3':
                    transfer_funds_init()
                else:
                    close_account()


# initializing banking system
database_connection()
menu_viewer()
