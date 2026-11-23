import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView } from 'react-native';
import { Card, Button } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';

export const AdminAttendanceMonitorScreen: React.FC = () => {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Attendance Monitor</Text>
          <Text style={styles.subtitle}>Branch biometrics & punch feeds</Text>
        </View>

        <Card>
          <Text style={styles.cardTitle}>Biometric Sync Status</Text>
          <Text style={styles.cardSub}>All eSSL machines online and operational</Text>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Connected Devices:</Text>
            <Text style={styles.statusVal}>4 / 4 Active</Text>
          </View>
          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Last Heartbeat:</Text>
            <Text style={styles.statusVal}>Just now</Text>
          </View>
        </Card>

        <Card>
          <Text style={styles.cardTitle}>Today's Realtime Punches</Text>
          <Text style={styles.cardSub}>Latest biometric transactions</Text>
          <View style={styles.punchItem}>
            <Text style={styles.punchEmp}>EMP001 - Rahul Sharma</Text>
            <Text style={styles.punchMeta}>Main Branch • 09:12 AM (IN)</Text>
          </View>
          <View style={styles.punchItem}>
            <Text style={styles.punchEmp}>EMP014 - Priya Nair</Text>
            <Text style={styles.punchMeta}>North Hub • 09:18 AM (IN)</Text>
          </View>
          <View style={styles.punchItem}>
            <Text style={styles.punchEmp}>EMP032 - Suresh Kumar</Text>
            <Text style={styles.punchMeta}>Main Branch • 09:25 AM (IN - Late)</Text>
          </View>
        </Card>
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
    marginBottom: Spacing.md,
  },
  title: {
    fontSize: Typography.sizes.lg,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  subtitle: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.secondary,
    marginTop: 2,
  },
  cardTitle: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  cardSub: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginBottom: Spacing.sm,
  },
  statusRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 4,
  },
  statusLabel: {
    fontSize: Typography.sizes.sm,
    color: Colors.text.secondary,
  },
  statusVal: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.semibold,
    color: Colors.primary[600],
  },
  punchItem: {
    paddingVertical: Spacing.xs,
    borderTopWidth: 1,
    borderTopColor: Colors.neutral[100],
    marginTop: 4,
  },
  punchEmp: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.semibold,
    color: Colors.text.primary,
  },
  punchMeta: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
  },
});
