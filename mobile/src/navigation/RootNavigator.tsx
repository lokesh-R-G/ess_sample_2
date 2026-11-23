import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { ActivityIndicator, View } from 'react-native';
import { useAuth } from '../store/AuthContext';
import { Colors } from '../theme/colors';
import { MainTabNavigator } from './TabNavigator';
import { LoginScreen } from '../screens/auth/LoginScreen';
import { ChangePasswordScreen } from '../screens/auth/ChangePasswordScreen';
import { MobilePunchScreen } from '../screens/attendance/MobilePunchScreen';
import { ApplyLeaveScreen } from '../screens/leave/ApplyLeaveScreen';
import { ReimbursementsScreen } from '../screens/reimbursement/ReimbursementScreen';
import { NotificationsScreen } from '../screens/notifications/NotificationsScreen';
import { AdminDashboardScreen } from '../screens/admin/AdminDashboardScreen';
import { AdminEmployeesScreen } from '../screens/admin/AdminEmployeesScreen';
import { AdminLeaveApprovalsScreen } from '../screens/admin/AdminLeaveApprovalsScreen';
import { AdminAttendanceMonitorScreen } from '../screens/admin/AdminAttendanceMonitorScreen';
import { AdminPayrollCyclesScreen } from '../screens/admin/AdminPayrollCyclesScreen';

const Stack = createNativeStackNavigator();

export const RootNavigator: React.FC = () => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: Colors.background.light }}>
        <ActivityIndicator size="large" color={Colors.primary[500]} />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {!isAuthenticated ? (
          <Stack.Screen name="Login" component={LoginScreen} />
        ) : user?.firstLogin ? (
          <Stack.Screen name="ChangePassword" component={ChangePasswordScreen} />
        ) : (
          <>
            <Stack.Screen name="MainTabs" component={MainTabNavigator} />
            <Stack.Screen
              name="MobilePunch"
              component={MobilePunchScreen}
              options={{ headerShown: true, title: 'Mobile Punch' }}
            />
            <Stack.Screen
              name="ApplyLeave"
              component={ApplyLeaveScreen}
              options={{ headerShown: true, title: 'Apply for Leave' }}
            />
            <Stack.Screen
              name="Reimbursements"
              component={ReimbursementsScreen}
              options={{ headerShown: true, title: 'Expense Claims' }}
            />
            <Stack.Screen
              name="Notifications"
              component={NotificationsScreen}
              options={{ headerShown: true, title: 'Notifications' }}
            />
            <Stack.Screen
              name="AdminDashboard"
              component={AdminDashboardScreen}
              options={{ headerShown: true, title: 'Admin Overview' }}
            />
            <Stack.Screen
              name="AdminEmployees"
              component={AdminEmployeesScreen}
              options={{ headerShown: true, title: 'Employee Directory' }}
            />
            <Stack.Screen
              name="AdminLeaveApprovals"
              component={AdminLeaveApprovalsScreen}
              options={{ headerShown: true, title: 'Leave Approvals' }}
            />
            <Stack.Screen
              name="AdminAttendanceMonitor"
              component={AdminAttendanceMonitorScreen}
              options={{ headerShown: true, title: 'Attendance Monitor' }}
            />
            <Stack.Screen
              name="AdminPayrollCycles"
              component={AdminPayrollCyclesScreen}
              options={{ headerShown: true, title: 'Payroll Cycles' }}
            />
            <Stack.Screen
              name="ChangePasswordModal"
              component={ChangePasswordScreen}
              options={{ headerShown: true, title: 'Change Password' }}
            />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
};
