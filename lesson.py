#print("Результат: ", 7, 15, sep="", end="!\n")
#print('Вторая линия')
#print('Результат:', 5 // 3) - округление в меньшую сторону, round(5 / 2) -  в ближайшую
#print('Результат:', max(5, 6, -1, 0, 4, -54, 12)) - находит максимальное значение, а min - минимальное
#print('Результат:', abs(-4)) - модуль
#print('Результат:', pow(5, 2)) - степень(также как и 5 ** 2)

number = 5 # int

digit = 4.5 # float
word = 'Результат: ' # string
boolean = True # bool
str_num = '5' #string

#print(word + str(digit))
print()
del number

number = 7 
print(number + int(str_num))
print(word + str(number + int(str_num)))




num1 = int(input('Введите первое число: '))

num2 = int(input('Введите второе число: '))

num1 -= 5

print('Результат: ', num1 + num2)
print('Результат: ', num1 - num2)
print('Результат: ', num1 / num2)
print('Результат: ', num1 * num2)
print('Результат: ', num1 ** num2)

word = 'привет'
print(word * 20)