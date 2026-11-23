import React from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView } from 'react-native';
import { Card, Button, StatusBadge } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';

export const AdminPayrollCyclesScreen: React.FC = () => {
  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Payroll Cycles</Text>
          <Text style={styles.subtitle}>Monthly salary batch execution & review</Text>
        </View>

        <Card>
          <View style={styles.cycleHeader}>
            <Text style={styles.cycleTitle}>November 2026 Cycle</Text>
            <StatusBadge status="DRAFT" />
          </View>
          <Text style={styles.cycleSub}>Period: 01 Nov 2026 - 30 Nov 2026</Text>
          <View style={styles.cycleStats}>
            <View>
              <Text style={styles.statLbl}>Employees</Text>
              <Text style={styles.statVal}>48</Text>
            </View>
            <View>
              <Text style={styles.statLbl}>Estimated Net</Text>
              <Text style={styles.statVal}>₹18,45,200</Text>
            </View>
          </View>
          <Button
            title="Review & Calculate"
            style={{ marginTop: Spacing.sm }}
            onPress={() => {}}
          />
        </Card>

        <Card>
          <View style={styles.cycleHeader}>
            <Text style={styles.cycleTitle}>October 2026 Cycle</Text>
            <StatusBadge status="PUBLISHED" />
          </View>
          <Text style={styles.cycleSub}>Period: 01 Oct 2026 - 31 Oct 2026</Text>
          <View style={styles.cycleStats}>
            <View>
              <Text style={styles.statLbl}>Employees</Text>
              <Text style={styles.statVal}>48</Text>
            </View>
            <View>
              <Text style={styles.statLbl}>Total Net Disbursed</Text>
              <Text style={styles.statVal}>₹18,22,400</Text>
            </View>
          </View>
          <Button
            title="Download Bank Export"
            variant="outline"
            style={{ marginTop: Spacing.sm }}
            onPress={() => {}}
          />
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
  cycleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  cycleTitle: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  cycleSub: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: 2,
  },
  cycleStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginVertical: Spacing.sm,
    backgroundColor: Colors.neutral[50],
    padding: Spacing.sm,
    borderRadius: Spacing.borderRadius.md,
  },
  statLbl: {
    fontSize: 10,
    color: Colors.text.muted,
  },
  statVal: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
    marginTop: 2,
  },
});
