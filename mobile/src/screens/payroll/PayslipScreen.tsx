import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, SafeAreaView, TouchableOpacity, Alert } from 'react-native';
import { Card, StatusBadge, Button } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { getMyPayslips } from '../../services/payrollService';
import { PayslipRecord } from '../../types/payroll';

export const PayslipScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [payslips, setPayslips] = useState<PayslipRecord[]>([]);
  const [loading, setLoading] = useState(false);

  const loadPayslips = async () => {
    try {
      setLoading(true);
      const res = await getMyPayslips();
      setPayslips(res);
    } catch {
      // Error handling
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadPayslips();
  }, []);

  const handleDownload = (item: PayslipRecord) => {
    Alert.alert('Download Payslip', `Initiating PDF download for ${item.monthName} ${item.year}`);
  };

  const renderPayslip = ({ item }: { item: PayslipRecord }) => (
    <Card style={styles.payslipCard}>
      <View style={styles.cardHeader}>
        <View>
          <Text style={styles.monthText}>{item.monthName} {item.year}</Text>
          <Text style={styles.paidDaysText}>Paid Days: {item.paidDays} | LOP: {item.lossOfPayDays}</Text>
        </View>
        <StatusBadge status={item.status} />
      </View>

      <View style={styles.salaryRow}>
        <View style={styles.salaryCol}>
          <Text style={styles.salaryLabel}>Gross Earnings</Text>
          <Text style={styles.salaryAmount}>₹{item.grossEarnings.toLocaleString('en-IN')}</Text>
        </View>
        <View style={styles.salaryCol}>
          <Text style={styles.salaryLabel}>Total Deductions</Text>
          <Text style={[styles.salaryAmount, { color: Colors.status.error }]}>
            -₹{item.totalDeductions.toLocaleString('en-IN')}
          </Text>
        </View>
        <View style={styles.salaryCol}>
          <Text style={styles.salaryLabel}>Net Payout</Text>
          <Text style={[styles.salaryAmount, { color: Colors.primary[600], fontWeight: '700' }]}>
            ₹{item.netSalary.toLocaleString('en-IN')}
          </Text>
        </View>
      </View>

      <Button
        title="Download PDF"
        variant="outline"
        onPress={() => handleDownload(item)}
        style={styles.downloadBtn}
      />
    </Card>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={payslips}
        keyExtractor={(item) => item.id}
        renderItem={renderPayslip}
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadPayslips} colors={[Colors.primary[500]]} />}
        ListHeaderComponent={
          <View style={styles.header}>
            <Text style={styles.title}>Payslip History</Text>
            <Text style={styles.subtitle}>View and download your monthly salary statements</Text>
          </View>
        }
        ListEmptyComponent={
          !loading ? (
            <Card style={styles.emptyCard}>
              <Text style={styles.emptyText}>No payslips published yet.</Text>
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
  payslipCard: {
    marginBottom: Spacing.md,
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.sm,
  },
  monthText: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  paidDaysText: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: 2,
  },
  salaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: Colors.neutral[50],
    padding: Spacing.sm,
    borderRadius: Spacing.borderRadius.md,
    marginVertical: Spacing.xs,
  },
  salaryCol: {
    alignItems: 'center',
  },
  salaryLabel: {
    fontSize: 10,
    color: Colors.text.muted,
    marginBottom: 2,
  },
  salaryAmount: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.semibold,
    color: Colors.text.primary,
  },
  downloadBtn: {
    height: 38,
    marginTop: Spacing.sm,
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
