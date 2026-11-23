# 05. Authentication and Role-Based Access Control (RBAC)

## 1. Authentication Lifecycle
1. **User Login (`/v1/auth/login/`):**
   - The user inputs their Employee ID and Password.
   - On success, the API returns `accessToken`, `role`, and flags (`firstLogin`, `mustChangePassword`).
   - The mobile client immediately stores the token securely in persistent device storage.
   - The app fetches `/v1/auth/me/` to retrieve the complete user profile and granular permissions ledger.
2. **Forced Password Change:**
   - If `firstLogin` or `mustChangePassword` is true, the user is immediately routed to the `ChangePassword` screen and blocked from accessing other screens until changed.
3. **Session Hydration & Auto-Login:**
   - On cold start, the app loads the token from secure storage.
   - Calls `/v1/auth/me/` in the background. If valid, user transitions directly to the home screen.
   - If invalid or expired (401), the storage is purged and the user is redirected to Login.
4. **Logout:**
   - Purges local token storage and cached user data, resetting navigation back to `Login`.

---

## 2. Role-Based Navigation & Permission Evaluation

### 2.1 Role Hierarchy
- **Roles:** `EMPLOYEE`, `ADMIN`, `SUPER_ADMIN`, `FLEET_MANAGER`, `STORE_MANAGER`.
- Employees default to `EmployeeTabs` (Dashboard, Attendance, Leave, Payslip, Profile).
- Users with administrative roles or permissions (`employee.read`, `leave.approve`, `payroll.read`, etc.) receive an additional **Admin Access** entry point in their profile/header or a dedicated Admin Drawer.

### 2.2 Granular Permission Engine (`hasPermission`)
Consistent with the web application's permission checker in `AuthContext.tsx`:
```typescript
hasPermission(permissionId: string): boolean {
  if (!user || !user.permissions) return false;
  const scopes = user.permissions[permissionId];
  if (!Array.isArray(scopes) || scopes.length === 0) return false;
  // If the only scope is 'SELF', it is employee-level access, not administrative
  if (scopes.length === 1 && scopes[0] === 'SELF') return false;
  return true;
}
```

### 2.3 Field-Level Editing Permissions
On the `Profile` screen, field edits are guarded by:
- `user.permissions.canEditMobile`
- `user.permissions.canEditAddress`
- `user.permissions.canEditBank`
- `user.permissions.canEditEmergencyContact`
Any field without permission is rendered read-only with a lock icon.
