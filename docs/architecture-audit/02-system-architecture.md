# 02 System Architecture

```mermaid
graph TD
    Client[Frontend SPA - TS/Vite] --> API[Backend - FastAPI]
    API --> Controller[Controllers]
    Controller --> Services[Services & Engines]
    Services --> Repositories[Prisma Repositories]
    Repositories --> DB[(Primary SQL DB)]
    
    Services --> eSSL[eSSL Biometric Integration]
```

*Note: Background workers (Celery/RQ) presence is minimal or not completely decoupled based on static analysis, meaning high-load tasks might currently execute synchronously or in simple background threads.*
