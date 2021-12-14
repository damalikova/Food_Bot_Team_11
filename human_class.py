import logging

from telegram import Bot, Update
from telegram.ext import CallbackContext, CommandHandler, Filters, MessageHandler, Updater


class User:

    def __init__(self, name, age, sex, height, weight, activity, goal):
        """Constructor"""
        self.name = name
        self.age = age
        self.sex = sex
        self.height = height
        self.weight = weight
        self.activity = activity
        self.goal = goal
        self.calorie_norm = 0
        self.protein_norm = 0
        self.fat_norm = 0
        self.carbohydrate_norm = 0


    def count_norm(self):
        """
        Counts daily norm of nutrients according to user's attributes
        Source: https://edatop.ru/252-raschet-bzhu.html#hmenu-10
        """
        
        activity_cf = {
            'нулевая': 1.2,
            'слабая': 1.375,
            'средняя': 1.55,
            'высокая': 1.7,
            'экстремальная': 1.9
        }

        # (proteins, fats, carbs) aka (б, ж, у)
        goal_cf = {
            'поддержание формы': (0.3, 0.3, 0.4),
            'похудение': (0.25, 0.25, 0.5),
            'набор массы': (0.35, 0.3, 0.55)
        }
        
        if self.sex == 'женский':
            self.calorie_norm = round(447.6 + 9.2 * self.weight + 3.1 * self.height - 4.3 * self.age)
        elif self.sex == 'мужской':
            self.calorie_norm = round(88.36 + 13.4 * self.weight + 4.8 * self.height - 5.7 * self.age)
        self.calorie_norm *= activity_cf[self.activity]

        # 1g protein = 4kcal, 1g carb = 4kcal, 1g fat = 9kcal
        self.protein_norm = round(self.calorie_norm * goal_cf[self.goal][0] / 4)
        self.fat_norm = round(self.calorie_norm * goal_cf[self.goal][1] / 9)
        self.carbohydrate_norm = round(self.calorie_norm * goal_cf[self.goal][2] / 4)

        return f'{self.name.title()}, ваша дневная норма калорий — {self.calorie_norm} ккал. \n' \
               f'Белки: {self.protein_norm} г. \n' \
               f'Жиры: {self.fat_norm} г. \n' \
               f'Углеводы: {self.carbohydrate_norm} г.'


    def meal(self):
        """
        Adds each dish to a database
        """
        pass


# just for check
username = input('Введите ваше имя: ')
user_age = int(input('Сколько вам лет? '))
user_sex = input('Укажите ваш пол: ')
user_height = int(input('Какой у вас рост? Введите число в сантиметрах: '))
user_weight = int(input('Какой у вас вес? Введите число в килограммах: '))
user_activity = input('Укажите ваш уровень активности (нулевая, слабая, средняя, высокая, экстремальная): ')
user_goal = input('Укажите вашу цель (поддержание формы, похудение, набор массы: ')

user = User(username, user_age, user_sex, user_height, user_weight, user_activity, user_goal)
print(user.count_norm())
