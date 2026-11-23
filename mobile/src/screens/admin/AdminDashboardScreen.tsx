import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, SafeAreaView, TouchableOpacity } from 'react-native';
import { Card, Button } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { getAdminSummary } from '../../services/adminService';
import { AdminSummaryStats } from '../../types/common';

export const AdminDashboardScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [stats, setStats] = useState<AdminSummaryStats | null>(null);
  const [loading, setLoading] = useState(false);

  const loadSummary = async () => {
    try {
      setLoading(true);
      const res = await getAdminSummary();
      setStats(res);
    } catch {
      // Graceful fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSummary();
  }, []);

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadSummary} colors={[Colors.primary[500]]} />}
      >
        <View style={styles.header}>
          <Text style={styles.title}>HRMS Administration</Text>
          <Text style={styles.subtitle}>Workforce overview and administrative tools</Text>
        </View>

        {/* Headcount & Today's Attendance */}
        <Text style={styles.sectionTitle}>Today's Workforce Stats</Text>
        <Card>
          <View style={styles.kpiRow}>
            <View style={styles.kpiCol}>
              <Text style={styles.kpiVal}>{stats?.totalEmployees ?? 0}</Text>
              <Text style={styles.kpiLbl}>Total Headcount</Text>
            </View>
            <View style={styles.kpiCol}>
              <Text style={[styles.kpiVal, { color: Colors.primary[500] }]}>{stats?.presentToday ?? 0}</Text>
              <Text style={styles.kpiLbl}>Present</Text>
            </View>
            <View style={styles.kpiCol}>
              <Text style={[styles.kpiVal, { color: Colors.status.error }]}>{stats?.absentToday ?? 0}</Text>
              <Text style={styles.kpiLbl}>Absent</Text>
            </View>
            <View style={styles.kpiCol}>
              <Text style={[styles.kpiVal, { color: Colors.status.info }]}>{stats?.onLeaveToday ?? 0}</Text>
              <Text style={styles.kpiLbl}>On Leave</Text>
            </View>
          </View>
        </Card>

        {/* Management Portals */}
        <Text style={styles.sectionTitle}>HRMS Operations</Text>

        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => navigation.navigate('AdminLeaveApprovals')}
        >
          <View style={styles.menuIconBadge}>
            <Text style={{ fontSize: 22 }}>📋</Text>
          </View>
          <View style={styles.menuTextCol}>
            <Text style={styles.menuTitle}>Leave Approvals Queue</Text>
            <Text style={styles.menuSub}>{stats?.pendingLeaveApprovals ?? 0} applications awaiting action</Text>
          </View>
          <Text style={styles.chevron}>➔</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => navigation.navigate('AdminEmployees')}
        >
          <View style={[styles.menuIconBadge, { backgroundColor: Colors.status.infoBg }]}>
            <Text style={{ fontSize: 22 }}>👥</Text>
          </View>
          <View style={styles.menuTextCol}>
            <Text style={styles.menuTitle}>Employee Directory</Text>
            <Text style={styles.menuSub}>Search, view and manage employee profiles</Text>
          </View>
          <Text style={styles.chevron}>➔</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => navigation.navigate('AdminAttendanceMonitor')}
        >
          <View style={[styles.menuIconBadge, { backgroundColor: Colors.primary[50] }]}>
            <Text style={{ fontSize: 22 }}>🕒</Text>
          </View>
          <View style={styles.menuTextCol}>
            <Text style={styles.menuTitle}>Attendance Monitor</Text>
            <Text style={styles.menuSub}>Live daily logs, sync status & regularization</Text>
          </View>
          <Text style={styles.chevron}>➔</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.menuItem}
          onPress={() => navigation.navigate('AdminPayrollCycles')}
        >
          <View style={[styles.menuIconBadge, { backgroundColor: Colors.status.warningBg }]}>
            <Text style={{ fontSize: 22 }}>💰</Text>
          </View>
          <View style={styles.menuTextCol}>
            <Text style={styles.menuTitle}>Payroll Cycles & Control</Text>
            <Text style={styles.menuSub}>Run monthly calculation, review drafts & exports</Text>
          </View>
          <Text style={styles.chevron}>➔</Text>
        </TouchableOpacity>
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
  header: {
    marginBottom: Spacing.lg,
  },
  title: {
    fontSize: Typography.sizes.xl,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  subtitle: {
    fontSize: Typography.sizes.sm,
    color: Colors.text.secondary,
    marginTop: 2,
  },
  sectionTitle: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
    marginBottom: Spacing.sm,
    marginTop: Spacing.md,
  },
  kpiRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingVertical: Spacing.xs,
  },
  kpiCol: {
    alignItems: 'center',
  },
  kpiVal: {
    fontSize: Typography.sizes.xl,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  kpiLbl: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: 2,
  },
  menuItem: {
    backgroundColor: Colors.neutral.white,
    padding: Spacing.md,
    borderRadius: Spacing.borderRadius.md,
    borderWidth: 1,
    borderColor: Colors.border.light,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  menuIconBadge: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.primary[100],
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  menuTextCol: {
    flex: 1,
  },
  menuTitle: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.semibold,
    color: Colors.text.primary,
  },
  menuSub: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: 2,
  },
  chevron: {
    fontSize: Typography.sizes.base,
    color: Colors.neutral[400],
  },
});
