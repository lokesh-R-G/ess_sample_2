import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, SafeAreaView, TouchableOpacity } from 'react-native';
import { Card, StatusBadge, Button } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { getMyAttendance } from '../../services/attendanceService';
import { AttendanceRecord, AttendanceSummary } from '../../types/attendance';

export const AttendanceScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [records, setRecords] = useState<AttendanceRecord[]>([]);
  const [summary, setSummary] = useState<AttendanceSummary | null>(null);
  const [loading, setLoading] = useState(false);

  const loadAttendance = async () => {
    try {
      setLoading(true);
      const res = await getMyAttendance();
      setRecords(res.records);
      setSummary(res.summary);
    } catch {
      // Error handling
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAttendance();
  }, []);

  const renderItem = ({ item }: { item: AttendanceRecord }) => (
    <Card style={styles.recordCard}>
      <View style={styles.recordHeader}>
        <Text style={styles.dateText}>{item.date}</Text>
        <StatusBadge status={item.status} />
      </View>
      <View style={styles.punchDetails}>
        <View style={styles.punchCol}>
          <Text style={styles.punchLabel}>Punch In</Text>
          <Text style={styles.punchTime}>{item.inTime || '--:--'}</Text>
        </View>
        <View style={styles.punchCol}>
          <Text style={styles.punchLabel}>Punch Out</Text>
          <Text style={styles.punchTime}>{item.outTime || '--:--'}</Text>
        </View>
        <View style={styles.punchCol}>
          <Text style={styles.punchLabel}>Total Hours</Text>
          <Text style={styles.punchTime}>
            {item.totalHours ? `${item.totalHours.toFixed(1)} hrs` : '--'}
          </Text>
        </View>
      </View>
    </Card>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={records}
        keyExtractor={(item, index) => item.id || `${item.date}-${index}`}
        renderItem={renderItem}
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadAttendance} colors={[Colors.primary[500]]} />}
        ListHeaderComponent={
          <View>
            <View style={styles.header}>
              <Text style={styles.title}>Daily Attendance</Text>
              <Button
                title="📍 Mobile Punch"
                onPress={() => navigation.navigate('MobilePunch')}
                style={{ height: 38 }}
              />
            </View>

            {summary && (
              <Card style={styles.summaryCard}>
                <View style={styles.summaryRow}>
                  <View style={styles.summaryItem}>
                    <Text style={styles.summaryValue}>{summary.presentDays}</Text>
                    <Text style={styles.summaryLabel}>Present</Text>
                  </View>
                  <View style={styles.summaryItem}>
                    <Text style={[styles.summaryValue, { color: Colors.status.error }]}>{summary.absentDays}</Text>
                    <Text style={styles.summaryLabel}>Absent</Text>
                  </View>
                  <View style={styles.summaryItem}>
                    <Text style={[styles.summaryValue, { color: Colors.status.warning }]}>{summary.lateArrivals}</Text>
                    <Text style={styles.summaryLabel}>Late</Text>
                  </View>
                  <View style={styles.summaryItem}>
                    <Text style={[styles.summaryValue, { color: Colors.status.info }]}>{summary.weeklyOffs}</Text>
                    <Text style={styles.summaryLabel}>Weekly Off</Text>
                  </View>
                </View>
              </Card>
            )}
          </View>
        }
        ListEmptyComponent={
          !loading ? (
            <Card style={styles.emptyCard}>
              <Text style={styles.emptyText}>No attendance records found for this period.</Text>
            </Card>
          ) : null
        }
      />
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
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  title: {
    fontSize: Typography.sizes.lg,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  summaryCard: {
    marginBottom: Spacing.lg,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryValue: {
    fontSize: Typography.sizes.xl,
    fontWeight: Typography.weights.bold,
    color: Colors.primary[500],
  },
  summaryLabel: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.secondary,
    marginTop: 2,
  },
  recordCard: {
    marginBottom: Spacing.sm,
  },
  recordHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  dateText: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.semibold,
    color: Colors.text.primary,
  },
  punchDetails: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingTop: Spacing.xs,
    borderTopWidth: 1,
    borderTopColor: Colors.neutral[100],
  },
  punchCol: {
    alignItems: 'flex-start',
  },
  punchLabel: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
  },
  punchTime: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.medium,
    color: Colors.text.primary,
    marginTop: 2,
  },
  emptyCard: {
    alignItems: 'center',
    paddingVertical: Spacing.xl,
  },
  emptyText: {
    color: Colors.text.muted,
    fontSize: Typography.sizes.sm,
  },
});
