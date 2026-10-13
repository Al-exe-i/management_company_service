# Развёртывание на тестовом сервере

## Структура каталогов

Backend и frontend остаются отдельными Git-репозиториями. Разместите их рядом:

```text
projects/
  uk_backend/
    docker-compose.yml
  uk_frontend/
    Dockerfile
```

Если frontend находится в другом месте, задайте `FRONTEND_CONTEXT` в `.docker.env`. Android-приложение собирается отдельно и в контейнер не помещается.

Нужны Docker Engine и Docker Compose v2.20 или новее. Все команды ниже выполняются в каталоге `uk_backend`.

## Настройки

```bash
cp .docker.env.example .docker.env
```

На Windows используйте `Copy-Item .docker.env.example .docker.env`. Задайте собственные `POSTGRES_PASSWORD` и `SECRET_KEY`. Для генерации секрета:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

`HTTP_PORT` по умолчанию равен `8080`. Порт PostgreSQL наружу не публикуется. Приложения обращаются к БД по имени сервиса `db`, а браузер — к API того же адреса, на котором открыт сайт. При обычном запуске через Nginx `CORS_ORIGINS=[]` достаточно. Для отдельного web-клиента укажите JSON-массив разрешённых адресов.

Файл `.docker.env` предназначен для Compose; прежний локальный `.env` backend в контейнер не копируется. Ключи Firebase, загруженные фотографии, `.git`, локальные окружения и зависимости исключены из Docker build context.

В БД время сохраняется в UTC; соединения приложения и миграций также используют UTC. Интерфейсы и бизнес-графики используют московское время, а контейнеры приложений настроены на `Europe/Moscow`.

## Первый запуск

```bash
docker compose --env-file .docker.env config --quiet
docker compose --env-file .docker.env up -d --build --wait
docker compose --env-file .docker.env ps -a
docker compose --env-file .docker.env logs migrate
```

Сначала PostgreSQL проходит проверку готовности. Затем одноразовый сервис `migrate` применяет Alembic-миграции. Только после успешного завершения запускаются backend, frontend и Nginx. Состояние `migrate: Exited (0)` нормально. При ошибке миграции backend не запускается; причину смотрите в `logs migrate`.

Compose использует имя проекта `management-company-test`, поэтому новый тестовый запуск не подхватывает старый volume локального Compose автоматически.

Создайте первого администратора:

```bash
docker compose --env-file .docker.env exec backend python -m app.cli.create_admin --login admin --name "Администратор"
```

Пароль запрашивается без отображения на экране. Повторный запуск при существующем администраторе завершится отказом и не изменит учётную запись. Демо-пользователи и стандартные пароли автоматически не добавляются. После входа добавьте дома, категории, пользователей, исполнителей и их графики. До появления исполнителя создание заявок ограничено действующими правилами системы.

Адреса:

- Web: `http://SERVER_IP:8080/`.
- REST API: `http://SERVER_IP:8080/api/v1/`.
- Swagger: `http://SERVER_IP:8080/docs`.
- Готовность API и БД: `http://SERVER_IP:8080/health/ready`.
- WebSocket: `ws://SERVER_IP:8080/api/v1/ws/updates`.

Для доступа через интернет настройте HTTPS на внешнем reverse proxy. При HTTPS web-клиент автоматически использует `wss`. Настройте передачу WebSocket Upgrade, исходного `Host` и `X-Forwarded-Proto` на внешнем proxy. Если внешний proxy находится на том же сервере, задайте `HTTP_BIND=127.0.0.1`.

В Android сейчас адрес сервера задаётся в `RetrofitClient.SERVER_BASE_URL`. Для тестового сервера укажите адрес Nginx, затем пересоберите APK. `127.0.0.1` на смартфоне без ADB reverse не является адресом удалённого сервера.

## Firebase

Базовый Compose работает без ключа: REST API и WebSocket доступны, Firebase push не отправляются.

Поместите service account JSON в `.secrets/firebase-service-account.json` и подключите дополнительный Compose-файл:

```bash
docker compose --env-file .docker.env -f docker-compose.yml -f docker-compose.firebase.yml config --quiet
docker compose --env-file .docker.env -f docker-compose.yml -f docker-compose.firebase.yml up -d --build --wait
```

Можно задать другой путь через `FCM_SERVICE_ACCOUNT_HOST_FILE`. Файл монтируется только в backend по адресу `/run/secrets/firebase_service_account`, в Docker-образ и Git он не попадает. На Linux ключ должен быть доступен для чтения UID `10001`, под которым работает backend; например:

```bash
chmod 700 .secrets
sudo chown 10001:10001 .secrets/firebase-service-account.json
sudo chmod 400 .secrets/firebase-service-account.json
```

Дальнейшие команды обновления используйте с тем же набором `-f`, чтобы не отключить Firebase случайно. Отправку настоящих push необходимо проверить с вашим Firebase-проектом и устройством.

## Обновление и данные

Получите новые версии обоих репозиториев. Перед обновлением сохраните БД и фотографии. Затем:

```bash
docker compose --env-file .docker.env stop gateway frontend backend
docker compose --env-file .docker.env build backend frontend
docker compose --env-file .docker.env run --rm migrate
docker compose --env-file .docker.env up -d --wait
```

Если миграция завершилась с ошибкой, не запускайте backend новой версии до исправления. Единственный процесс Uvicorn необходим для нынешнего WebSocket hub; увеличивать количество workers или реплик без общего брокера событий нельзя.

Данные PostgreSQL сохраняются в `postgres_data`, фотографии и фон авторизации — в `uploads`. Пересборка контейнеров и обычный `docker compose down` сохраняют volumes. `down -v` удаляет БД и фотографии.

Существующие данные локальной установки автоматически не переносятся. Для переноса нужны дамп PostgreSQL и содержимое каталога `static`. После восстановления дайте UID `10001` доступ к файлам volume и выполните миграции; `alembic stamp` для пропуска миграций не нужен.

## Резервное копирование

Пример для Linux, из каталога backend:

```bash
mkdir -p backups
docker compose --env-file .docker.env exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > backups/database.dump
docker compose --env-file .docker.env exec -T backend tar -czf - -C /app static > backups/static.tar.gz
```

Для согласованной копии остановите изменение данных на время создания дампа и архива. Каталог `backups` исключён из Git и Docker-образа.

## Проверка после запуска

Проверьте `/health/ready`, вход под созданным администратором, сохранение фотографии, создание заявки и её появление у диспетчера через WebSocket. Для Firebase дополнительно проверьте push на Android. Сборка контейнеров требует доступа к Docker Hub, GHCR, PyPI и npm registry.
