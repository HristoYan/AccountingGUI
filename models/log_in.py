# from app import db


class UserLog:
    def __init__(self, first_name: str, last_name: str, age: int, email: str, money: int, password: str):
        self.email = email
        self.age = age
        self.last_name = last_name
        self.first_name = first_name
        self._money = int(money)
        self._password = password

    @property
    def money(self):
        return self._money

    @money.setter
    def money(self, value):
        new_money = self._money + value
        self._money = new_money

    # def to_db(self):
    #     log_info = {
    #         'first_name': self.first_name,
    #         'last_name': self.last_name,
    #         'age': self.age,
    #         'email': self.email,
    #         'money': self._money,
    #         'password': self._password
    #     }
    #     db.execute("INSERT INTO users (first_name, last_name, age, email, money, password) "
    #                "VALUES (?, ?, ?, ?, ?, ?)", self.first_name, self.last_name, self.age, self.email,
    #                self.money, self._password)
    #     return 'Successful registration!'
