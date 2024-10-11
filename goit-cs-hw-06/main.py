""" 
Веб-додаток для обміну повідомленнями між користувачами. 
Дані зберігаються у базі даних MongoDB.
Застосування мультипроцесів дозволяє запускати HTTP-сервер та сокет-сервер одночасно.
HTTP-сервер відповідає за обробку HTTP-запитів, відправку статичних файлів та відправку даних на сокет-сервер.
Сокет-сервер приймає дані від HTTP-сервера, зберігає їх у MongoDB та виводить повідомлення про збереження.
"""


import json
import multiprocessing
import pathlib
import socket
from http.server import BaseHTTPRequestHandler
import socketserver
from datetime import datetime
from pymongo import MongoClient
import urllib.parse
import mimetypes


# Підключення до MongoDB
# Створюємо клієнт для взаємодії з колекцією "messages" у базі даних "message_db".
client = MongoClient('mongodb://mongo:27017/')
db = client['message_db']
messages_collection = db['messages']


# HTTP сервер
class MyHttpRequestHandler(BaseHTTPRequestHandler):
    # Метод для обробки GET запитів
    def do_GET(self):
        # Парсимо URL щоб визначити шлях
        pr_url = urllib.parse.urlparse(self.path)
        # Якщо шлях кореневий відправляємо index.html
        if pr_url.path == '/':
            self.send_html_file('index.html')
        # Якщо запит на сторінку message відправляємо message.html
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        # Для інших запитів перевіряємо чи існує відповідний статичний файл
        else:
            if pathlib.Path().joinpath('static', pr_url.path[1:]).exists():
                self.send_static()
            # Якщо файл не знайдено повертаємо помилку 404
            else:
                self.send_html_file('error.html', 404)


    # Метод для обробки POST запитів (наприклад, відправка форми)
    def do_POST(self):
        # Перевіряємо, чи запит на сторінку /message
        if self.path == "/message":
            # Отримуємо довжину контенту і читаємо дані з форми
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            # Розбираємо дані з форми у форматі key=value
            parsed_data = urllib.parse.parse_qs(post_data.decode('utf-8'))
            
            # Створюємо словник з отриманих даних (ім'я користувача та повідомлення)
            message_dict = {
                "username": parsed_data["username"][0],
                "message": parsed_data["message"][0]
            }
            # Відправляємо цей словник на сокет-сервер для обробки
            self.send_to_socket_server(message_dict)
            
            # Після відправки показуємо сторінку messageSent.html
            self.send_html_file('messageSent.html')
        # Якщо запит на інший шлях, повертаємо сторінку помилки
        else:
            self.send_html_file('error.html', 404)


    # Метод для відправки даних на сокет-сервер
    def send_to_socket_server(self, message_dict):
        # Створюємо TCP-з'єднання з сокет-сервером
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(('localhost', 5000))  # Підключення до сокет-сервера на порту 5000
            # Відправляємо дані JSON
            s.sendall(json.dumps(message_dict).encode())


    # Метод для відправки HTML-файлів
    def send_html_file(self, filename, status=200):
        # Відправляємо відповідь із зазначеним статусом
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # Читаємо і відправляємо HTML-файл
        with open(f'templates/{filename}', 'rb') as fd:
            self.wfile.write(fd.read())


    # Метод для відправки статичних файлів
    def send_static(self):
        # Відправляємо відповідь зі статусом 200 OK
        self.send_response(200)
        # Визначаємо MIME-тип файлу
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        # Читаємо і відправляємо файл
        with open(f'static/{self.path}', 'rb') as file:
            self.wfile.write(file.read())


# Сокет-сервер для прийому даних з HTTP сервера
def socket_server():
    # Створюємо сокет-сервер TCP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 5000))  # Прив'язуємо сокет до порту 5000
    server_socket.listen(5)  # Встановлюємо максимальну кількість одночасних з'єднань
    
    while True:
        # Приймаємо з'єднання від клієнта
        client_socket, address = server_socket.accept()
        print(f"Підключено клієнта з адресою: {address}")  # Виводимо адресу клієнта
        data = client_socket.recv(1024)  # Отримуємо до 1024 байт даних
        
        
        if data:
            # Розбираємо отримані дані з JSON у словник
            message_dict = json.loads(data.decode())
            # Додаємо до повідомлення поточну дату
            message_dict["date"] = str(datetime.now())
            # Зберігаємо повідомлення в MongoDB
            messages_collection.insert_one(message_dict)
            print(f"Збережено повідомлення від {message_dict['username']}")
        
        # Закриваємо з'єднання з клієнтом
        client_socket.close()


# Функція для запуску HTTP-сервера
def run_http_server():
    PORT = 3000  # Встановлюємо порт для HTTP-сервера
    handler = MyHttpRequestHandler  # Використовуємо наш клас обробника запитів
    # Запускаємо сервер на порту 3000
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("Сервер HTTP запущений на порту", PORT)
        httpd.serve_forever()

# Основний блок для запуску двох серверів
if __name__ == "__main__":
    # Створюємо процес для HTTP-сервера
    http_process = multiprocessing.Process(target=run_http_server)

    # Створюємо процес для сокет-сервера
    socket_process = multiprocessing.Process(target=socket_server)

    # Запускаємо процеси
    http_process.start()
    socket_process.start()

    # Очікуємо завершення процесів
    http_process.join()
    socket_process.join()
