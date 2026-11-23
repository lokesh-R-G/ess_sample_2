# 03. Mobile Architecture & Directory Structure

## 1. Architectural Philosophy
The mobile architecture is built to mirror the production web application's rigor while following idiomatic React Native patterns for Android:
- **Separation of Concerns:** Business logic and data fetching reside in `services/` and `hooks/`, isolated from UI presentation screens and components.
- **Single Source of Truth:** The backend REST API is the authoritative state. No mock fixtures or divergent calculations are implemented.
- **Type Safety:** Full TypeScript end-to-end schemas matching backend Pydantic models.
- **Offline & Token Persistence:** Tokens and authenticated session information are stored securely on the device using platform-appropriate secure storage abstractions.

---

## 2. Directory Structure

```
mobile/
├── android/                 # Native Android Gradle Project
│   ├── app/
│   │   ├── build.gradle
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       └── java/com/esshrms/app/MainActivity.kt
│   ├── build.gradle
│   ├── settings.gradle
│   └── gradle.properties
├── src/
│   ├── api/                 # Axios / Fetch client, token interceptors, base URL config
│   │   ├── client.ts
│   │   └── config.ts
│   ├── assets/              # App icons, splash images, brand vectors
│   ├── components/          # Reusable native UI components
│   │   ├── common/          # Button, Input, Card, Badge, Modal, LoadingIndicator, EmptyState
│   │   ├── layout/          # ScreenContainer, Header, TabBar, BottomSheet
│   │   └── modules/         # Domain-specific components (AttendanceCard, LeaveBalanceCard, etc.)
│   ├── config/              # Environment & build configs (Development / Staging / Production)
│   ├── constants/           # Colors, typography, spacing, route names
│   ├── hooks/               # Custom hooks (useAuth, useAttendance, useLeave, usePermissions)
│   ├── navigation/          # React Navigation Stacks, Tabs & Drawers
│   │   ├── RootNavigator.tsx
│   │   ├── AuthNavigator.tsx
│   │   ├── AppNavigator.tsx
│   │   ├── TabNavigator.tsx
│   │   └── AdminNavigator.tsx
│   ├── screens/             # Screen implementations
│   │   ├── auth/
│   │   ├── dashboard/
│   │   ├── attendance/
│   │   ├── leave/
│   │   ├── payroll/
│   │   ├── profile/
│   │   ├── reimbursement/
│   │   ├── notifications/
│   │   └── admin/
│   ├── services/            # API service layer mirroring web `src/services/`
│   │   ├── authService.ts
│   │   ├── attendanceService.ts
│   │   ├── leaveService.ts
│   │   ├── payrollService.ts
│   │   ├── profileService.ts
│   │   ├── reimbursementService.ts
│   │   └── adminService.ts
│   ├── store/               # Global state (Auth Context / State Container)
│   │   └── AuthContext.tsx
│   ├── theme/               # Design tokens, color palette, typography definitions
│   │   ├── colors.ts
│   │   ├── typography.ts
│   │   └── spacing.ts
│   ├── types/               # TypeScript interfaces & API contracts
│   │   ├── auth.ts
│   │   ├── attendance.ts
│   │   ├── leave.ts
│   │   ├── payroll.ts
│   │   ├── employee.ts
│   │   └── navigation.ts
│   └── utils/               # Formatting, date utilities, validation, error parsers
├── docs/                    # Phase documentation
├── App.tsx                  # Root entry point with Providers
├── package.json
└── tsconfig.json
```

---

## 3. Technology Stack & Key Libraries
- **Framework:** React Native 0.74+ / Expo Bare workflow compatible
- **Language:** TypeScript 5+
- **Navigation:** `@react-navigation/native`, `@react-navigation/native-stack`, `@react-navigation/bottom-tabs`
- **Layout & Safe Area:** `react-native-safe-area-context`, `react-native-screens`
- **Networking:** Custom robust Fetch API / Axios client with automatic Bearer token injection and 401 handling
- **Storage:** Secure persistent storage with asynchronous storage fallback
- **Icons:** `@expo/vector-icons` (MaterialCommunityIcons, Ionicons, Feather)
- **Forms & Validation:** React Hook Form & Zod schema validation
