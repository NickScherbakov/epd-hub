# EPD-Hub Frontend

Интеллектуальная платформа мониторинга электронных перевозочных документов (ЭПД)

## 📁 Структура проекта

```
frontend/
├── index.html          # Главная страница
├── package.json        # Конфигурация проекта
├── sw.js              # Service Worker для offline поддержки
├── css/
│   ├── styles.css     # Основные стили
│   └── responsive.css # Адаптивный дизайн
├── js/
│   └── main.js        # Основной скрипт
└── assets/            # Статические ресурсы (изображения, шрифты и т.д.)
```

## 🚀 Быстрый старт

### Локальная разработка (простой способ)

```bash
# Перейдите в директорию frontend
cd frontend

# Запустите простой HTTP сервер
python -m http.server 8080

# Откройте браузер
# http://localhost:8080
```

### С использованием Docker

```bash
# Из корневой директории проекта
docker-compose up -d

# Frontend будет доступен по адресу: http://localhost:8000
```

### Node.js (если требуется)

```bash
# Установите зависимости
npm install

# Запустите dev сервер
npm run dev

# Создайте production сборку (если нужна)
npm run build
```

## 📋 Функциональность

### ✅ Завершено
- [x] Главная страница (Landing Page)
- [x] Секция с ключевыми возможностями
- [x] Описание процесса работы платформы
- [x] Информация о целевой аудитории
- [x] Технологический стек
- [x] Call-to-Action секции
- [x] Адаптивный дизайн (мобильные, планшеты, десктопы)
- [x] Service Worker для offline поддержки
- [x] API status widget с real-time проверкой
- [x] Keyboard shortcuts (Alt+D, Alt+A, Alt+G)

### 🔄 В разработке
- [ ] Интеграция с Next.js или React
- [ ] Авторизация и личный кабинет
- [ ] Dashboard с документами
- [ ] Система уведомлений
- [ ] Профиль пользователя

### 📋 Планируется
- [ ] PWA функциональность
- [ ] Offline режим с синхронизацией
- [ ] Мультиязычная поддержка
- [ ] Темная тема
- [ ] Аналитика

## 🎨 Дизайн и стили

### Цветовая схема

- **Основной цвет (Primary):** `#2e7d32` (зеленый)
- **Вторичный цвет (Secondary):** `#1a1a2e` (темный синий)
- **Акцентный цвет (Accent):** `#ff6b35` (оранжевый)
- **Фон:** `#f5f5f5` (светло-серый)
- **Текст:** `#1a1a2e` (темный)

### Адаптивность

Сайт полностью адаптивен и работает на:
- 📱 Мобильные устройства (320px и выше)
- 📱 Планшеты (769px - 1024px)
- 💻 Настольные компьютеры (1025px и выше)
- 🖥️ Большие экраны (1440px и выше)
- 🌙 Dark mode (если поддерживается браузером)

## 🔧 Функции JavaScript

### API Communication

```javascript
// Проверить статус API
await window.EPDHub.checkAPIStatus();

// Форматировать дату
window.EPDHub.formatDate(new Date());

// Debounce функция
const debouncedFunc = window.EPDHub.debounce(callback, 300);
```

### Keyboard Shortcuts

- **Alt + D** — Открыть документацию
- **Alt + A** — Открыть API документацию (Swagger)
- **Alt + G** — Открыть GitHub репозиторий

### Service Worker

Service Worker автоматически кэширует:
- Статические файлы (CSS, JS)
- HTML страницы
- API ответы (с fallback на кэш при offline)

Для разработки Service Worker работает автоматически после загрузки страницы.

## 📊 Производительность

### Оптимизация

- Минимальные CSS/JS файлы
- Ленивая загрузка изображений
- Кэширование через Service Worker
- Сжатие изображений

### Monitoring

Приложение автоматически мониторит:
- Время загрузки страницы
- Время отклика API
- Статус API

Это можно отслеживать в консоли браузера.

## 🌐 API Integration

Frontend по умолчанию обращается к:
```
http://localhost:8000
```

Это можно изменить в файле `js/main.js`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## 📱 SEO и Meta теги

Страница включает:
- Meta description
- Open Graph tags (при необходимости можно добавить)
- Favicon (при необходимости можно добавить)
- Schema.org структурированные данные

## 🧪 Тестирование

### Проверка производительности

1. Откройте DevTools (F12)
2. Перейдите на вкладку "Performance"
3. Нажмите "Record" и перезагрузите страницу
4. Анализируйте результаты

### Проверка адаптивности

1. Откройте DevTools (F12)
2. Нажмите Ctrl+Shift+M (илиCmd+Shift+M на Mac)
3. Выберите разные типы устройств

### Проверка Service Worker

1. Откройте DevTools (F12)
2. Перейдите на вкладку "Application"
3. В левом меню выберите "Service Workers"

## 📦 Zависимости

Frontend использует только встроенные браузерные API:
- Fetch API
- Service Worker API
- Intersection Observer API
- LocalStorage API

Никаких внешних библиотек не требуется!

## 🚀 Deployment

### На GitHub Pages

```bash
# Скопируйте содержимое frontend в docs/
cp -r frontend/* docs/

# Используйте GitHub Pages для deploy
```

### На простом веб-сервере

```bash
# Просто скопируйте все файлы из frontend/
scp -r frontend/* user@server:/var/www/html/epd-hub/
```

### С Docker

```bash
docker-compose up -d
```

## 🐛 Troubleshooting

### API не подключается

Убедитесь, что:
1. FastAPI сервер запущен: `uvicorn app.main:app --reload`
2. Адрес API правильный в `js/main.js`
3. CORS включен на сервере (уже включен по умолчанию)

### Service Worker не работает

1. Service Worker работает только на https (или localhost)
2. Проверьте DevTools → Application → Service Workers
3. Очистите кэш: DevTools → Application → Storage → Clear site data

### Стили не загружаются

1. Проверьте, что файлы CSS находятся в директории `css/`
2. Очистите кэш браузера (Ctrl+Shift+Delete)
3. Проверьте пути в `index.html`

## 📞 Контакты и поддержка

- GitHub: https://github.com/NickScherbakov/epd-hub
- Issues: https://github.com/NickScherbakov/epd-hub/issues

## 📄 Лицензия

MIT License - смотрите [LICENSE](../LICENSE)

---

**EPD-Hub Frontend** — Современный интерфейс для управления электронными перевозочными документами 🚀
