import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, SafeAreaView, Alert } from 'react-native';
import { Card, Button, StatusBadge } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { getAdminPendingLeaves, approveOrRejectLeave } from '../../services/adminService';

export const AdminLeaveApprovalsScreen: React.FC = () => {
  const [leaves, setLeaves] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [actingId, setActingId] = useState<string | null>(null);

  const loadLeaves = async () => {
    try {
      setLoading(true);
      const res = await getAdminPendingLeaves();
      setLeaves(res);
    } catch {
      // Graceful error handling
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLeaves();
  }, []);

  const handleAction = async (id: string, action: 'APPROVE' | 'REJECT') => {
    try {
      setActingId(id);
      await approveOrRejectLeave(id, action, `${action}d from Mobile App`);
      Alert.alert('Action Recorded', `Leave application has been ${action.toLowerCase()}d.`);
      loadLeaves();
    } catch (err: any) {
      Alert.alert('Action Error', err.message || 'Failed to update leave application');
    } finally {
      setActingId(null);
    }
  };

  const renderItem = ({ item }: { item: any }) => (
    <Card style={styles.card}>
      <View style={styles.header}>
        <View>
          <Text style={styles.empName}>{item.employeeName || item.employeeCode || 'Employee'}</Text>
          <Text style={styles.empSub}>{item.department || 'Operations'} • {item.leaveTypeName || 'Leave'}</Text>
        </View>
        <StatusBadge status={item.status || 'PENDING'} />
      </View>

      <Text style={styles.dates}>
        📅 {item.startDate} to {item.endDate} ({item.totalDays || 1} days)
      </Text>
      <Text style={styles.reason} numberOfLines={2}>
        Reason: {item.reason || 'Personal'}
      </Text>

      <View style={styles.actionRow}>
        <Button
          title="Approve"
          onPress={() => handleAction(item.id, 'APPROVE')}
          loading={actingId === item.id}
          style={[styles.actionBtn, { backgroundColor: Colors.primary[500] }]}
        />
        <Button
          title="Reject"
          variant="danger"
          onPress={() => handleAction(item.id, 'REJECT')}
          disabled={actingId === item.id}
          style={styles.actionBtn}
        />
      </View>
    </Card>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={leaves}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadLeaves} colors={[Colors.primary[500]]} />}
        ListHeaderComponent={
          <View style={styles.listHeader}>
            <Text style={styles.screenTitle}>Leave Approval Requests</Text>
            <Text style={styles.screenSub}>Review pending leave applications from your team</Text>
          </View>
        }
        ListEmptyComponent={
          !loading ? (
            <Card style={styles.emptyCard}>
              <Text style={styles.emptyText}>No pending leave requests.</Text>
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
  listHeader: {
    marginBottom: Spacing.md,
  },
  screenTitle: {
    fontSize: Typography.sizes.lg,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  screenSub: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.secondary,
    marginTop: 2,
  },
  card: {
    marginBottom: Spacing.sm,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  empName: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  empSub: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: 2,
  },
  dates: {
    fontSize: Typography.sizes.sm,
    color: Colors.text.secondary,
    marginTop: Spacing.xs,
  },
  reason: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: 2,
  },
  actionRow: {
    flexDirection: 'row',
    marginTop: Spacing.md,
    paddingTop: Spacing.xs,
    borderTopWidth: 1,
    borderTopColor: Colors.neutral[100],
  },
  actionBtn: {
    flex: 1,
    height: 38,
    marginHorizontal: Spacing.xs,
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
