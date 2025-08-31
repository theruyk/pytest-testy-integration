# pytest-testy-integration

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Pytest](https://img.shields.io/badge/pytest-6.0+-green.svg)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pytest plugin for seamless integration with TestY Test Management System. Automatically sync test execution results with TestY TMS.

*[Russian version below / Русская версия ниже](#русская-версия)*

## 🌟 Features

- 🔗 **Automatic synchronization** of test results with TestY TMS
- 🏷️ **Test case mapping** using simple decorators
- 📊 **Complete support** for all pytest outcomes (passed/failed/skipped/broken)
- 🔧 **Standalone installation** - no pip package required, just copy files
- ⚙️ **Environment-based configuration** via .env file
- 🚀 **Easy setup** - works out of the box with minimal configuration
- 📱 **Mobile testing support** - works with Appium and mobile test frameworks
- 🎯 **Multiple test cases** - link one test to multiple TestY cases

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install pytest requests python-dotenv
```

### Step 2: Download Plugin Files

Place these files in your test directory:

```
Project/
├── tests/
│   ├── testy_plugin.py    # ← TestY Plugin
│   ├── conftest.py        # ← Pytest Configuration  
│   └── test_example.py    # ← Your Tests
├── .env                   # ← Connection Settings
└── requirements.txt
```

**conftest.py content:**
```python
pytest_plugins = ["testy_plugin"]
```

### Step 3: Configure Environment

Create `.env` file in project root:

```env
TESTY_URL=https://your-testy-instance.com
TESTY_PROJECT_ID=your_project_id
TESTY_USERNAME=your_username
TESTY_PASSWORD=your_password
```

### Step 4: Write Tests

```python
# tests/test_example.py
from testy_plugin import testy

@testy.id(1156)
def test_api_authorization():
    """API authorization test"""
    # Your test logic here
    assert True

@testy.id(1157, 1158)
def test_multiple_cases():
    """Test linked to multiple test cases"""
    # Result will be sent to both cases
    assert True

def test_without_testy():
    """Regular test without TestY integration"""
    assert 2 + 2 == 4
```

### Step 5: Run Tests

```bash
pytest --testy --testy-plan=YOUR_PLAN_ID
```

## 📋 Command Line Options

### Required Parameters:
- `--testy` - enables TestY TMS integration
- `--testy-plan=<ID>` - TestY test plan ID

### Usage Examples:

```bash
# Basic run
pytest --testy --testy-plan=105

# With Allure reporting
pytest --alluredir=./allure-results --testy --testy-plan=105

# Mobile testing with device
pytest --device=pixel_8 --testy --testy-plan=105

# Verbose output
pytest -v --testy --testy-plan=105

# Run specific test file
pytest tests/test_api.py --testy --testy-plan=105

# With parallel execution
pytest -n 2 --testy --testy-plan=105
```

## 🎯 Using @testy.id() Decorator

### Single Test Case:
```python
@testy.id(1156)
def test_single_case():
    assert True
```

### Multiple Test Cases:
```python
@testy.id(1156, 1157, 1158)
def test_multiple_cases():
    # Result will be sent to all specified cases
    assert True
```

### Without Decorator:
```python
def test_regular_test():
    # Regular pytest test, result won't be sent to TestY
    assert True
```

## 📊 Test Status Mapping

| Pytest Result | TestY Status | Comment |
|---------------|--------------|---------|
| ✅ **Passed** | Passed (ID: 2) | "Автотест выполнен успешно" |
| ❌ **Failed/Error** | Failed (ID: 1) | "Тест завершился с ошибкой: {details}" |
| ⏭️ **Skipped** | Skipped (ID: 3) | "Тест пропущен: {reason}" |

## 🔍 Example Output

```bash
$ pytest tests/ --testy --testy-plan=105

TestY: Successfully authenticated as test_user
TestY: Loading tests from plan 105...
TestY: Integration enabled. Loaded 5 tests from plan 105

tests/test_api.py::test_login PASSED
TestY: Result sent for test 1156 (case 1): Passed

tests/test_api.py::test_logout FAILED
TestY: Result sent for test 1157 (case 2): Failed

tests/test_api.py::test_permissions SKIPPED
TestY: Result sent for test 1158 (case 3): Skipped
```

## 🐛 Troubleshooting

### Check Plugin Loading:
```bash
pytest --help
```
Should show "testy" section with `--testy` and `--testy-plan` options.

### Debug Output:
```bash
pytest -v -s --tb=short --testy --testy-plan=105
```

### Common Issues:

1. **"TestY authentication failed"**
   - Check your `.env` file settings
   - Verify user credentials in TestY

2. **"Test case X not found in plan Y"**
   - Ensure test case is added to the plan
   - Verify you're using correct case ID (not instance ID)

3. **Plugin not loading**
   - Check `conftest.py` is in tests directory
   - Verify `testy_plugin.py` is in the same folder

## 🔧 TestY API Endpoints

The plugin uses these TestY API endpoints:

- **POST** `/api/token/obtain/` - authentication
- **GET** `/api/v2/tests/` - get tests from plan  
- **POST** `/api/v2/results/` - send test results

## 📝 How It Works

1. **Initialization**: Plugin activates when `--testy` flag is used
2. **Authentication**: Gets access token via TestY API
3. **Test Loading**: Retrieves test cases from specified plan
4. **Execution**: Pytest runs tests normally
5. **Result Reporting**: After each test with `@testy.id()`, result is sent to TestY

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

# Русская версия

## 🌟 Возможности

- 🔗 **Автоматическая синхронизация** результатов тестов с TestY TMS
- 🏷️ **Привязка тест-кейсов** через простые декораторы
- 📊 **Полная поддержка** всех исходов pytest (passed/failed/skipped/broken)
- 🔧 **Автономная установка** - не требует pip пакета, просто скопируйте файлы
- ⚙️ **Конфигурация через переменные окружения** в .env файле
- 🚀 **Простая настройка** - работает сразу после минимальной конфигурации
- 📱 **Поддержка мобильного тестирования** - работает с Appium и мобильными фреймворками
- 🎯 **Множественные тест-кейсы** - привязка одного теста к нескольким кейсам TestY

## 🚀 Быстрый старт

### Шаг 1: Установите зависимости

```bash
pip install pytest requests python-dotenv
```

### Шаг 2: Скачайте файлы плагина

Поместите эти файлы в папку с тестами:

```
Проект/
├── tests/
│   ├── testy_plugin.py    # ← Плагин TestY
│   ├── conftest.py        # ← Конфигурация pytest  
│   └── test_example.py    # ← Ваши тесты
├── .env                   # ← Настройки подключения
└── requirements.txt
```

**Содержимое conftest.py:**
```python
pytest_plugins = ["testy_plugin"]
```

### Шаг 3: Настройте окружение

Создайте файл `.env` в корне проекта:

```env
TESTY_URL=https://your-testy-instance.com
TESTY_PROJECT_ID=ваш_project_id
TESTY_USERNAME=ваш_логин
TESTY_PASSWORD=ваш_пароль
```

### Шаг 4: Напишите тесты

```python
# tests/test_example.py
from testy_plugin import testy

@testy.id(1156)
def test_api_authorization():
    """Тест авторизации API"""
    # Логика вашего теста
    assert True

@testy.id(1157, 1158)
def test_multiple_cases():
    """Тест связанный с несколькими кейсами"""
    # Результат будет отправлен в оба кейса
    assert True

def test_without_testy():
    """Обычный тест без интеграции TestY"""
    assert 2 + 2 == 4
```

### Шаг 5: Запустите тесты

```bash
pytest --testy --testy-plan=ВАШ_PLAN_ID
```

## 📋 Параметры командной строки

### Обязательные параметры:
- `--testy` - включает интеграцию с TestY TMS
- `--testy-plan=<ID>` - ID тест-плана в TestY

### Примеры использования:

```bash
# Базовый запуск
pytest --testy --testy-plan=105

# С отчетом Allure
pytest --alluredir=./allure-results --testy --testy-plan=105

# Мобильное тестирование с устройством
pytest --device=pixel_8 --testy --testy-plan=105

# Подробный вывод
pytest -v --testy --testy-plan=105

# Запуск конкретного файла
pytest tests/test_api.py --testy --testy-plan=105

# С параллельным выполнением
pytest -n 2 --testy --testy-plan=105
```

## 🎯 Использование декоратора @testy.id()

### Один тест-кейс:
```python
@testy.id(1156)
def test_single_case():
    assert True
```

### Несколько тест-кейсов:
```python
@testy.id(1156, 1157, 1158)
def test_multiple_cases():
    # Результат отправится во все указанные кейсы
    assert True
```

### Без декоратора:
```python
def test_regular_test():
    # Обычный pytest тест, результат не отправляется в TestY
    assert True
```

## 📊 Сопоставление статусов

| Результат pytest | Статус TestY | Комментарий |
|------------------|--------------|-------------|
| ✅ **Passed** | Passed (ID: 2) | "Автотест выполнен успешно" |
| ❌ **Failed/Error** | Failed (ID: 1) | "Тест завершился с ошибкой: {детали}" |
| ⏭️ **Skipped** | Skipped (ID: 3) | "Тест пропущен: {причина}" |

## 🔍 Пример вывода

```bash
$ pytest tests/ --testy --testy-plan=105

TestY: Successfully authenticated as test_user
TestY: Loading tests from plan 105...
TestY: Integration enabled. Loaded 5 tests from plan 105

tests/test_api.py::test_login PASSED
TestY: Result sent for test 1156 (case 1): Passed

tests/test_api.py::test_logout FAILED
TestY: Result sent for test 1157 (case 2): Failed

tests/test_api.py::test_permissions SKIPPED
TestY: Result sent for test 1158 (case 3): Skipped
```

## 🐛 Устранение неполадок

### Проверка загрузки плагина:
```bash
pytest --help
```
Должна появиться секция "testy" с опциями `--testy` и `--testy-plan`.

### Отладочный вывод:
```bash
pytest -v -s --tb=short --testy --testy-plan=105
```

### Частые проблемы:

1. **"TestY authentication failed"**
   - Проверьте настройки в `.env` файле
   - Убедитесь в корректности учетных данных

2. **"Test case X not found in plan Y"**
   - Убедитесь, что тест-кейс добавлен в план
   - Проверьте, что используете ID кейса, а не инстанса

3. **Плагин не загружается**
   - Проверьте наличие `conftest.py` в папке с тестами
   - Убедитесь, что `testy_plugin.py` в той же папке

## 🔧 API эндпоинты TestY

Плагин использует следующие эндпоинты TestY API:

- **POST** `/api/token/obtain/` - авторизация
- **GET** `/api/v2/tests/` - получение тестов из плана  
- **POST** `/api/v2/results/` - отправка результатов тестов

## 📱 Интеграция с мобильным тестированием

```bash
# Appium + TestY + Allure
pytest --device=pixel_8 --alluredir=./allure-results --testy --testy-plan=105

# Множественные устройства
pytest --device=pixel_8 --device=iphone_14 --testy --testy-plan=105
```

## 📝 Как это работает

1. **Инициализация**: Плагин активируется при использовании флага `--testy`
2. **Авторизация**: Получение токена доступа через API TestY
3. **Загрузка тестов**: Получение тест-кейсов из указанного плана
4. **Выполнение**: Pytest выполняет тесты в обычном режиме
5. **Отправка результатов**: После каждого теста с `@testy.id()` результат отправляется в TestY

## 💡 Советы по использованию

### Комбинация с другими маркерами:
```python
@pytest.mark.ui
@pytest.mark.smoke
@testy.id(100, 101)
def test_critical_ui():
    assert True
```

## 🤝 Участие в разработке

1. Форкните репозиторий
2. Создайте ветку для новой функциональности (`git checkout -b feature/amazing-feature`)
3. Зафиксируйте изменения (`git commit -m 'Add amazing feature'`)
4. Отправьте в ветку (`git push origin feature/amazing-feature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект распространяется под лицензией MIT - подробности в файле [LICENSE](LICENSE).


### v1.0.0
- ✨ Первоначальный релиз
- 🔗 Базовая интеграция с TestY TMS
- 🏷️ Поддержка декоратора @testy.id()
- 📊 Автоматическая отправка результатов
- ⏭️ Поддержка skipped тестов

---

## 🌟 Звездочка

Если плагин оказался полезным, поставьте ⭐ этому репозиторию!