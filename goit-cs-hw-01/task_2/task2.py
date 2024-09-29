"""
Цей код реалізує базовий інтерпретатор арифметичних виразів. Інтерпретатор - це програма, яка аналізує (розбирає) вхідний текстовий рядок, 
складає його у структуроване дерево та виконує відповідні операції.

У процесі побудови цього інтерпретатора ми реалізуємо три основні компоненти:

Лексер (Lexer): Розділяє вхідний рядок на послідовність токенів (лексем), кожен з яких відповідає певному елементу виразу.

Парсер (Parser): Будує синтаксичне дерево (AST - Abstract Syntax Tree), яке відображає структуру та порядок виконання операцій у виразі.

Інтерпретатор (Interpreter): Виконує обчислення на основі синтаксичного дерева, визначаючи порядок і виконуючи математичні операції.

"""


# Визначення власних винятків, які будуть використовуватися для обробки помилок
class LexicalError(Exception):
    pass  # Лексична помилка при розпізнаванні токенів


class ParsingError(Exception):
    pass  # Синтаксична помилка при розборі виразів


# Типи токенів, які визначають можливі елементи математичного виразу
class TokenType:
    INTEGER = "INTEGER"  # Цілі числа, наприклад, "2", "345"
    PLUS = "PLUS"  # Символ "+"
    MINUS = "MINUS"  # Символ "-"
    MUL = "MUL"  # Символ "*"
    DIV = "DIV"  # Символ "/"
    LPAREN = "LPAREN"  # Ліва дужка "("
    RPAREN = "RPAREN"  # Права дужка ")"
    EOF = "EOF"  # Кінець тексту, щоб позначити завершення обробки


# Клас, що представляє токени (лексеми) в тексті
class Token:
    def __init__(self, type, value):
        self.type = type  # Тип токена (наприклад, INTEGER, PLUS тощо)
        self.value = value  # Значення токена (наприклад, "3", "+")

    def __str__(self):
        # Створює текстове представлення токена для відладки
        return f"Token({self.type}, {repr(self.value)})"


# Лексер, який розбиває вхідний текст на токени (лексеми)
class Lexer:
    def __init__(self, text):
        self.text = text  # Вхідний рядок виразу
        self.pos = 0  # Поточна позиція в тексті
        self.current_char = self.text[self.pos]  # Поточний символ для обробки

    def advance(self):
        # Переміщує поточну позицію вперед, щоб перейти до наступного символу
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None  # Якщо досягнуто кінця тексту, встановлюється None
        else:
            self.current_char = self.text[self.pos]  # Оновлює поточний символ

    def skip_whitespace(self):
        # Пропускає пробіли та інші непотрібні символи
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def integer(self):
        # Збирає послідовність цифр у ціле число
        result = ""
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)  # Повертає цілочисельне значення

    def get_next_token(self):
        # Головний метод для отримання наступного токена з вхідного рядка
        while self.current_char is not None:
            # Пропуск пробілів
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            # Якщо символ є цифрою, зчитується ціле число
            if self.current_char.isdigit():
                return Token(TokenType.INTEGER, self.integer())

            # Обробка математичних операторів
            if self.current_char == "+":
                self.advance()
                return Token(TokenType.PLUS, "+")
            if self.current_char == "-":
                self.advance()
                return Token(TokenType.MINUS, "-")
            if self.current_char == "*":
                self.advance()
                return Token(TokenType.MUL, "*")
            if self.current_char == "/":
                self.advance()
                return Token(TokenType.DIV, "/")
            if self.current_char == "(":
                self.advance()
                return Token(TokenType.LPAREN, "(")
            if self.current_char == ")":
                self.advance()
                return Token(TokenType.RPAREN, ")")

            # Якщо символ не розпізнано, викликається помилка
            raise LexicalError("Лексична помилка: невідомий символ")

        # Повертається токен EOF, коли всі символи оброблено
        return Token(TokenType.EOF, None)


# Абстрактне синтаксичне дерево (AST) - базовий клас
class AST:
    pass


# Вузол AST для операцій (додавання, віднімання, множення, ділення)
class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left  # Лівий операнд
        self.op = op  # Оператор (токен типу PLUS, MINUS тощо)
        self.right = right  # Правий операнд


# Вузол AST для чисел
class Num(AST):
    def __init__(self, token):
        self.token = token  # Токен, що представляє число
        self.value = token.value  # Значення числа


# Парсер, який будує синтаксичне дерево (AST) з токенів
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer  # Лексер для отримання токенів
        self.current_token = self.lexer.get_next_token()  # Поточний токен для обробки

    def error(self):
        raise ParsingError("Синтаксична помилка: очікується інший токен")

    def eat(self, token_type):
        # Споживає токен, якщо він відповідає очікуваному типу, або викликає помилку
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        # Обробка чисел та виразів у дужках
        token = self.current_token
        if token.type == TokenType.INTEGER:
            self.eat(TokenType.INTEGER)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()  # Рекурсивно обробляється вираз у дужках
            self.eat(TokenType.RPAREN)
            return node

    def term(self):
        # Обробка множення та ділення
        node = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        # Обробка додавання та віднімання
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)

            node = BinOp(left=node, op=token, right=self.term())

        return node


# Інтерпретатор, який обчислює значення виразу на основі побудованого синтаксичного дерева
class Interpreter:
    def __init__(self, parser):
        self.parser = parser

    def visit_BinOp(self, node):
        # Обчислення операцій додавання, віднімання, множення та ділення
        if node.op.type == TokenType.PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == TokenType.MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == TokenType.MUL:
            return self.visit(node.left) * self.visit(node.right)
        elif node.op.type == TokenType.DIV:
            try:
                return self.visit(node.left) / self.visit(node.right)
            except ZeroDivisionError:
                raise Exception("Ділення на нуль")

    def visit_Num(self, node):
        # Повертає значення числового токена
        return node.value

    def interpret(self):
        # Запуск обробки виразу, побудова та обчислення синтаксичного дерева
        tree = self.parser.expr()
        return self.visit(tree)

    def visit(self, node):
        # Динамічний виклик методу для обробки конкретного типу вузла AST
        method_name = "visit_" + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Помилка, якщо не знайдено відповідного методу для вузла AST
        raise Exception(f"Метод відвідування не визначений: visit_{type(node).__name__}")
    

# Тестування роботи інтерпретатора на різних виразах
def test_interpreter():
    test_cases = [
        "3 + 5",             # Просте додавання
        "10 - 2",            # Просте віднімання
        "7 * 4",             # Множення
        "8 / 2",             # Ділення
        "(3 + 5) * 2",       # Вираз із дужками та множенням
        "14 + 2 * 3 - 6 / 2" # Комбінований вираз з усіма операціями
    ]

    # Перебираємо всі тестові приклади та обчислюємо результат
    for expression in test_cases:
        lexer = Lexer(expression)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print(f"{expression} = {result}")


# Тестування 
test_interpreter()

""" 
output:

3 + 5 = 8
10 - 2 = 8
7 * 4 = 28
8 / 2 = 4.0
(3 + 5) * 2 = 16
14 + 2 * 3 - 6 / 2 = 17.0

"""
