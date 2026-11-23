import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, SafeAreaView, TouchableOpacity } from 'react-native';
import { Card, StatusBadge, Button } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { getLeaveData } from '../../services/leaveService';
import { LeaveApplication, LeaveBalanceItem } from '../../types/leave';

export const LeaveScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [balances, setBalances] = useState<LeaveBalanceItem[]>([]);
  const [applications, setApplications] = useState<LeaveApplication[]>([]);
  const [loading, setLoading] = useState(false);

  const loadLeaves = async () => {
    try {
      setLoading(true);
      const res = await getLeaveData();
      setBalances(res.balances);
      setApplications(res.applications);
    } catch {
      // Error handling
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeaves();
  }, []);

  const renderApplication = ({ item }: { item: LeaveApplication }) => (
    <Card style={styles.appCard}>
      <View style={styles.appHeader}>
        <Text style={styles.appType}>{item.leaveTypeName}</Text>
        <StatusBadge status={item.status} />
      </View>
      <Text style={styles.appDates}>
        {item.startDate} to {item.endDate} ({item.totalDays} {item.totalDays === 1 ? 'day' : 'days'})
      </Text>
      <Text style={styles.appReason} numberOfLines={2}>
        Reason: {item.reason}
      </Text>
      {Boolean(item.approverRemarks) && (
        <Text style={styles.approverRemarks}>
          Remarks: {item.approverRemarks}
        </Text>
      )}
    </Card>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={applications}
        keyExtractor={(item) => item.id}
        renderItem={renderApplication}
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadLeaves} colors={[Colors.primary[500]]} />}
        ListHeaderComponent={
          <View>
            <View style={styles.header}>
              <Text style={styles.title}>Leave Management</Text>
              <Button
                title="+ Apply Leave"
                onPress={() => navigation.navigate('ApplyLeave')}
                style={{ height: 38 }}
              />
            </View>

            <Text style={styles.sectionTitle}>Leave Balances</Text>
            <View style={styles.balanceGrid}>
              {balances.map((b) => (
                <View key={b.leaveTypeId} style={styles.balanceCard}>
                  <Text style={styles.balanceCode}>{b.code}</Text>
                  <Text style={styles.balanceAvailable}>{b.available}</Text>
                  <Text style={styles.balanceTotal}>of {b.totalAllocated} days</Text>
                </View>
              ))}
            </View>

            <Text style={styles.sectionTitle}>Application History</Text>
          </View>
        }
        ListEmptyComponent={
          !loading ? (
            <Card style={styles.emptyCard}>
              <Text style={styles.emptyText}>No leave applications yet.</Text>
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
  sectionTitle: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
    marginBottom: Spacing.sm,
    marginTop: Spacing.sm,
  },
  balanceGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: Spacing.md,
  },
  balanceCard: {
    backgroundColor: Colors.neutral.white,
    borderRadius: Spacing.borderRadius.md,
    padding: Spacing.md,
    borderWidth: 1,
    borderColor: Colors.border.light,
    minWidth: 100,
    flex: 1,
    marginRight: Spacing.sm,
    alignItems: 'center',
  },
  balanceCode: {
    fontSize: Typography.sizes.xs,
    fontWeight: Typography.weights.bold,
    color: Colors.text.secondary,
  },
  balanceAvailable: {
    fontSize: Typography.sizes.xxl,
    fontWeight: Typography.weights.bold,
    color: Colors.primary[500],
    marginVertical: 2,
  },
  balanceTotal: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
  },
  appCard: {
    marginBottom: Spacing.sm,
  },
  appHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  appType: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.semibold,
    color: Colors.text.primary,
  },
  appDates: {
    fontSize: Typography.sizes.sm,
    color: Colors.text.secondary,
    marginBottom: Spacing.xs,
  },
  appReason: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
  },
  approverRemarks: {
    fontSize: Typography.sizes.xs,
    color: Colors.status.info,
    marginTop: Spacing.xs,
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
