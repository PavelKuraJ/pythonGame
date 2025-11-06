# простая игра "Угадай число"

import random

def play():
    low, high = 1, 100
    number = random.randint(low, high)
    attempts = 0
    print(f"Я загадал число от {low} до {high}. Попробуй угадать!")
    while True:
        attempts += 1
        try:
            guess = int(input("Твой ответ: "))
        except ValueError:
            print("Пожалуйста, введи целое число.")
            continue
        if guess < number:
            print("Слишком мало.")
        elif guess > number:
            print("Слишком много.")
        else:
            print(f"Правильно! Ты потратил(а) {attempts} попыток.")
            break