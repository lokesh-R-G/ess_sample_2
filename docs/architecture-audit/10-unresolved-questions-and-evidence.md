# 10 Unresolved Questions And Evidence

- **Database Logs**: We need production database logs to confirm N+1 query patterns.
- **eSSL Integration Details**: Is it a direct database connection or an API poll? Need code inspection of eSSL workers.
- **Caching**: Are there existing Redis implementations not immediately visible in `app/main.py`?
