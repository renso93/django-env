Redis integration and deployment notes

This project supports using Redis as the Django cache backend for production. The settings already check for a `REDIS_URL` environment variable and use `django-redis` if present.

1) Requirements

Add to your project's requirements (example `requirements.txt`):

- django-redis

We added a suggestion line to `requirements.txt` already. To install:

```bash
pip install -r requirements.txt
# or install django-redis only
pip install django-redis
```

2) Environment variable

Set `REDIS_URL` in your environment. Example values:

- Without password (local):
  REDIS_URL=redis://127.0.0.1:6379/1

- With password:
  REDIS_URL=redis://:yourpassword@redis-host:6379/1

3) Example Docker Compose (Redis + Django)

Below is a minimal example `docker-compose.yml` snippet showing Redis and a Django web service.

```yaml
version: '3.8'
services:
  redis:
    image: redis:7
    restart: always
    volumes:
      - redis-data:/data
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn blog.wsgi:application --bind 0.0.0.0:8000
    env_file: .env
    environment:
      - REDIS_URL=redis://redis:6379/1
    depends_on:
      - redis
    ports:
      - "8000:8000"

volumes:
  redis-data:
```

Make sure your `.env` file (or environment) contains secrets (SECRET_KEY etc.).

4) Production checklist

- Install `django-redis` in your production environment.
- Set `REDIS_URL` to your Redis instance URL.
- Adjust cache timeout values to fit your needs.
- Consider using Redis for session storage as well by configuring `SESSION_ENGINE` and `SESSION_CACHE_ALIAS`.
- Monitor Redis memory usage and eviction policy.

5) Notes

- The current settings fall back to `locmem` cache if `REDIS_URL` is not set — suitable for development and tests, not for multi-process production.
- If you run multiple web workers (Gunicorn/uwsgi), `locmem` will not be shared between processes; use Redis in that case.

If you want, I can add an example `systemd` unit file or Ansible snippet to provision Redis and configure the ENV for production. Let me know which deployment platform you use.
