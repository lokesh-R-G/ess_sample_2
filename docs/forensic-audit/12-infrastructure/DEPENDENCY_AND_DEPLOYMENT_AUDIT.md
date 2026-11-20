# Dependency and Deployment Audit

## 1. Infrastructure Architecture
- Multi-container environment via docker-compose.yml.
- Dockerfile.backend: Python FastAPI container.
- Dockerfile.frontend: Node.js / Vite build with Nginx reverse proxy.

## 2. Observations and Vulnerabilities
- Dual backend path configuration in Dockerfile vs local development (/app vs /backend).
- Outdated npm packages in package.json flagged for Puppeteer and Chromium dependencies.
- Redacted environment templates checked in .env.example.
