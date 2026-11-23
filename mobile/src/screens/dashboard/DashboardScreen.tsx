import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, TouchableOpacity, SafeAreaView } from 'react-native';
import { useAuth } from '../../store/AuthContext';
import { Card, Button, StatusBadge } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { getMyAttendance } from '../../services/attendanceService';
import { getLeaveData } from '../../services/leaveService';
import { getMyPayslips } from '../../services/payrollService';
import { AttendanceSummary } from '../../types/attendance';
import { LeaveBalanceItem } from '../../types/leave';

export const DashboardScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const { user } = useAuth();
  const [refreshing, setRefreshing] = useState(false);
  const [attendanceSummary, setAttendanceSummary] = useState<AttendanceSummary | null>(null);
  const [leaveBalances, setLeaveBalances] = useState<LeaveBalanceItem[]>([]);
  const [latestNetPay, setLatestNetPay] = useState<number | null>(null);

  const loadDashboardData = async () => {
    try {
      const [attRes, leaveRes, payRes] = await Promise.all([
        getMyAttendance(),
        getLeaveData(),
        getMyPayslips(),
      ]);
      setAttendanceSummary(attRes.summary);
      setLeaveBalances(leaveRes.balances);
      if (payRes.length > 0) {
        setLatestNetPay(payRes[0].netSalary);
      }
    } catch {
      // Graceful fallback
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const fullName = user?.personal?.firstName 
    ? `${user.personal.firstName} ${user.personal.lastName || ''}`.trim() 
    : user?.empId || 'Employee';

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={[Colors.primary[500]]} />}
      >
        {/* Welcome Header */}
        <View style={styles.welcomeCard}>
          <Text style={styles.greeting}>Welcome back,</Text>
          <Text style={styles.userName}>{fullName}</Text>
          <Text style={styles.userRole}>
            {user?.employment?.designation || 'Staff'} • {user?.employment?.department || 'Operations'}
          </Text>
        </View>

        {/* Quick Actions */}
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionsRow}>
          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('MobilePunch')}
          >
            <View style={[styles.actionIconBadge, { backgroundColor: Colors.primary[50] }]}>
              <Text style={{ fontSize: 20 }}>📍</Text>
            </View>
            <Text style={styles.actionLabel}>Punch In/Out</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('ApplyLeave')}
          >
            <View style={[styles.actionIconBadge, { backgroundColor: Colors.status.infoBg }]}>
              <Text style={{ fontSize: 20 }}>📝</Text>
            </View>
            <Text style={styles.actionLabel}>Apply Leave</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.actionButton}
            onPress={() => navigation.navigate('Reimbursements')}
          >
            <View style={[styles.actionIconBadge, { backgroundColor: Colors.status.warningBg }]}>
              <Text style={{ fontSize: 20 }}>💳</Text>
            </View>
            <Text style={styles.actionLabel}>Expenses</Text>
          </TouchableOpacity>
        </View>

        {/* Attendance Summary */}
        <Text style={styles.sectionTitle}>This Month's Attendance</Text>
        <Card>
          <View style={styles.kpiGrid}>
            <View style={styles.kpiItem}>
              <Text style={styles.kpiValue}>{attendanceSummary?.presentDays ?? 0}</Text>
              <Text style={styles.kpiLabel}>Present</Text>
            </View>
            <View style={styles.kpiItem}>
              <Text style={[styles.kpiValue, { color: Colors.status.error }]}>
                {attendanceSummary?.absentDays ?? 0}
              </Text>
              <Text style={styles.kpiLabel}>Absent</Text>
            </View>
            <View style={styles.kpiItem}>
              <Text style={[styles.kpiValue, { color: Colors.status.warning }]}>
                {attendanceSummary?.lateArrivals ?? 0}
              </Text>
              <Text style={styles.kpiLabel}>Late</Text>
            </View>
            <View style={styles.kpiItem}>
              <Text style={[styles.kpiValue, { color: Colors.status.info }]}>
                {attendanceSummary?.weeklyOffs ?? 0}
              </Text>
              <Text style={styles.kpiLabel}>Weekly Off</Text>
            </View>
          </View>
        </Card>

        {/* Leave Balances */}
        <Text style={styles.sectionTitle}>Leave Balance</Text>
        <Card>
          {leaveBalances.length === 0 ? (
            <Text style={styles.emptyText}>No leave policies assigned</Text>
          ) : (
            leaveBalances.map((item, index) => (
              <View key={item.leaveTypeId || index} style={styles.leaveRow}>
                <View>
                  <Text style={styles.leaveName}>{item.leaveTypeName}</Text>
                  <Text style={styles.leaveUsed}>Used: {item.used} | Pending: {item.pending}</Text>
                </View>
                <View style={styles.leaveBadge}>
                  <Text style={styles.leaveAvailable}>{item.available}</Text>
                  <Text style={styles.daysLabel}>days</Text>
                </View>
              </View>
            ))
          )}
        </Card>

        {/* Latest Payslip Highlight */}
        {latestNetPay !== null && (
          <>
            <Text style={styles.sectionTitle}>Latest Salary</Text>
            <Card style={styles.payrollCard}>
              <View>
                <Text style={styles.salaryTitle}>Net Payout</Text>
                <Text style={styles.salaryAmount}>₹{latestNetPay.toLocaleString('en-IN')}</Text>
              </View>
              <Button
                title="View Payslip"
                variant="outline"
                onPress={() => navigation.navigate('PayrollTab')}
                style={{ height: 38 }}
              />
            </Card>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background.light,
  },
  container: {
    padding: Spacing.screenPadding,
  },
  welcomeCard: {
    backgroundColor: Colors.primary[500],
    borderRadius: Spacing.borderRadius.lg,
    padding: Spacing.lg,
    marginBottom: Spacing.lg,
  },
  greeting: {
    color: Colors.primary[100],
    fontSize: Typography.sizes.sm,
  },
  userName: {
    color: Colors.neutral.white,
    fontSize: Typography.sizes.xl,
    fontWeight: Typography.weights.bold,
    marginTop: 2,
  },
  userRole: {
    color: Colors.primary[100],
    fontSize: Typography.sizes.xs,
    marginTop: 4,
  },
  sectionTitle: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
    marginBottom: Spacing.sm,
    marginTop: Spacing.sm,
  },
  actionsRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: Spacing.lg,
  },
  actionButton: {
    flex: 1,
    backgroundColor: Colors.neutral.white,
    borderRadius: Spacing.borderRadius.md,
    padding: Spacing.md,
    alignItems: 'center',
    marginHorizontal: Spacing.xs,
    borderWidth: 1,
    borderColor: Colors.border.light,
  },
  actionIconBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.xs,
  },
  actionLabel: {
    fontSize: Typography.sizes.xs,
    fontWeight: Typography.weights.medium,
    color: Colors.text.primary,
  },
  kpiGrid: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  kpiItem: {
    alignItems: 'center',
  },
  kpiValue: {
    fontSize: Typography.sizes.xxl,
    fontWeight: Typography.weights.bold,
    color: Colors.primary[500],
  },
  kpiLabel: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.secondary,
    marginTop: 2,
  },
  leaveRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: Spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: Colors.neutral[100],
  },
  leaveName: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.semibold,
    color: Colors.text.primary,
  },
  leaveUsed: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: 2,
  },
  leaveBadge: {
    alignItems: 'flex-end',
  },
  leaveAvailable: {
    fontSize: Typography.sizes.lg,
    fontWeight: Typography.weights.bold,
    color: Colors.primary[600],
  },
  daysLabel: {
    fontSize: 10,
    color: Colors.text.muted,
  },
  payrollCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  salaryTitle: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
  },
  salaryAmount: {
    fontSize: Typography.sizes.xl,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
    marginTop: 2,
  },
  emptyText: {
    fontSize: Typography.sizes.sm,
    color: Colors.text.muted,
    textAlign: 'center',
    paddingVertical: Spacing.sm,
  },
});
