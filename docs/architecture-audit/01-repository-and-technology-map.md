# 01 Repository And Technology Map

## Frontend
- **Path**: `c:\ess\ess_sample_2\` (root level TS/JS files, Vite config, package.json).
- **Stack**: TypeScript, Vite, Tailwind CSS.

## Backend
- **Path**: `c:\ess\ess_sample_2\backend\`
- **Stack**: Python, FastAPI.
- **ORM**: Prisma Python client (`schema.prisma`, though currently we rely on `schema_dump.json` for structure).
- **Core Modules**: `app/attendance_v2`, `app/payroll`, `app/salary`, `app/leave`, `app/organization`.

## Integration
- eSSL sync for biometric attendance.
