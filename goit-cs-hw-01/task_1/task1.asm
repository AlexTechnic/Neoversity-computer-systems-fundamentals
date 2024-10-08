; Програма демонструє базові концепції роботи з даними на асемблері, такі як:
; - Виконання арифметичних операцій із завантаженими значеннями змінних
; - Перетворення числових значень у формат ASCII для виведення
; - Використання функцій DOS для відображення тексту та чисел на екран
; - Завершення виконання програми та повернення керування системі DOS

org  0x100               ; Вказуємо, що ця програма завантажується з адреси 0x100.
                         ; Це стандартне місце завантаження для програм у форматі .COM,
                         ; оскільки перші 0x100 байт у пам'яті зарезервовані для таблиці PSP (Program Segment Prefix).

section .data
    a db 5               ; Визначаємо змінну `a`, яка зберігає значення 5 (1 байт).
    b db 3               ; Визначаємо змінну `b`, яка зберігає значення 3 (1 байт).
    c db 2               ; Визначаємо змінну `c`, яка зберігає значення 2 (1 байт).
    resultMsg db 'Result: $' ; Визначаємо рядок `resultMsg`, який містить текст для виведення
                         ; при відображенні результату. Символ `$` в кінці вказує на завершення
                         ; рядка для функції DOS 09h, яка використовується для виводу рядка.

section .text
_start:
    ; Обчислення арифметичного виразу: a + (b - c)
    mov al, [b]          ; Завантажуємо значення `b` у регістр `al`.
                         ; `al` є 8-бітовим регістром (молодшою половиною регістру `ax`).
                         ; Тепер `al` містить значення 3.

    sub al, [c]          ; Віднімаємо значення `c` від `al`.
                         ; Тепер `al` = `b - c`, тобто `3 - 2 = 1`.

    add al, [a]          ; Додаємо значення `a` до `al`.
                         ; Тепер `al` = `a + (b - c)`, тобто `5 + 1 = 6`.

    ; Перетворення результату в ASCII символ
    add al, 30h          ; Перетворюємо результат в ASCII символ.
                         ; Значення `30h` є ASCII-кодом символу '0'. Додавання цього значення до
                         ; `al` дозволяє отримати ASCII-код для цифри, яка представляє результат.
                         ; Наприклад, якщо `al` = 6, то `al` стане `36h`, що є ASCII-кодом символу '6'.

    ; Виведення результату (текстовий рядок "Result: ")
    mov ah, 09h          ; Встановлюємо `ah` на 09h, що є кодом функції DOS для виведення рядка.
    lea dx, resultMsg    ; Завантажуємо адресу рядка `resultMsg` в регістр `dx`.
                         ; `lea` (Load Effective Address) використовується для завантаження адреси даних.
    int 21h              ; Викликаємо переривання `21h`, яке виконує функцію DOS, що вказана в `ah`.
                         ; Виводить текст "Result: ".

    ; Виведення самого результату
    mov dl, al           ; Переміщуємо значення `al` (результат обчислення) в `dl`.
                         ; Регістр `dl` використовується для виведення окремого символу.
    mov ah, 02h          ; Встановлюємо `ah` на 02h, що є кодом функції DOS для виведення символу.
    int 21h              ; Викликаємо переривання `21h`, яке виводить символ, що зберігається в `dl`.
                         ; У даному випадку це ASCII-код символу '6'.

    ; Завершення програми
    mov ax, 4c00h        ; Встановлюємо `ax` на 4c00h, що є кодом функції DOS для завершення програми.
                         ; 4Ch - код завершення програми, а 00h - код виходу (exit code).
    int 21h              ; Викликаємо переривання `21h`, яке завершує виконання програми
                         ; і повертає керування системі DOS.