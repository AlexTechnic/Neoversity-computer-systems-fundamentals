# !/bin/bash

# chmod +x script.sh

# Створюємо список вебсайтів для перевірки
sites=(
  "https://google.com"
  "https://edu.goit.global"
)

# Визначаємо назву файлу для збереження результатів перевірки
logfile="websites_stat.log"

# Очищаємо файл логів перед записом нових результатів
> "$logfile"

# Функція для перевірки статусу сайту
check_site() {
    status_code=$(curl -L -s -o /dev/null -w "%{http_code}" "$1")
    
    if [ "$status_code" -eq "200" ]; then
        echo "$1 is online" | tee -a "$logfile"
    else
        echo "$1 is offline" | tee -a "$logfile"
    fi
}

# Перебираємо сайти зі списку та викликаємо функцію check_site
for site in "${sites[@]}"; do
  check_site "$site"
done

# Виводимо повідомлення про запис результатів у лог
echo "Результати записані у файл $logfile"