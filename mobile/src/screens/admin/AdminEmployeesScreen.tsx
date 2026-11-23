import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, SafeAreaView } from 'react-native';
import { Card, StatusBadge, Input } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { getAdminEmployees } from '../../services/adminService';

export const AdminEmployeesScreen: React.FC = () => {
  const [employees, setEmployees] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);

  const loadEmployees = async () => {
    try {
      setLoading(true);
      const res = await getAdminEmployees();
      setEmployees(res);
    } catch {
      // Graceful error handling
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadEmployees();
  }, []);

  const filtered = employees.filter((emp) => {
    const term = search.toLowerCase();
    const name = `${emp.firstName || ''} ${emp.lastName || ''}`.toLowerCase();
    const code = (emp.employeeCode || emp.empId || '').toLowerCase();
    const dept = (emp.department || '').toLowerCase();
    return name.includes(term) || code.includes(term) || dept.includes(term);
  });

  const renderItem = ({ item }: { item: any }) => (
    <Card style={styles.card}>
      <View style={styles.row}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {(item.firstName || 'E').charAt(0).toUpperCase()}
          </Text>
        </View>
        <View style={styles.infoCol}>
          <Text style={styles.name}>{item.firstName} {item.lastName}</Text>
          <Text style={styles.sub}>{item.employeeCode || item.empId} • {item.designation || 'Staff'}</Text>
          <Text style={styles.dept}>{item.department || 'Operations'} | {item.branch || 'Main Branch'}</Text>
        </View>
        <StatusBadge status={item.status || 'ACTIVE'} />
      </View>
    </Card>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={filtered}
        keyExtractor={(item, index) => item.id || `${item.empId}-${index}`}
        renderItem={renderItem}
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadEmployees} colors={[Colors.primary[500]]} />}
        ListHeaderComponent={
          <View style={styles.header}>
            <Text style={styles.title}>Employee Directory</Text>
            <Input
              placeholder="Search by name, ID or department"
              value={search}
              onChangeText={setSearch}
            />
          </View>
        }
        ListEmptyComponent={
          !loading ? (
            <Card style={styles.emptyCard}>
              <Text style={styles.emptyText}>No employees matched your query.</Text>
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
    marginBottom: Spacing.sm,
  },
  card: {
    marginBottom: Spacing.sm,
  },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: Colors.primary[100],
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: Spacing.md,
  },
  avatarText: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.bold,
    color: Colors.primary[700],
  },
  infoCol: {
    flex: 1,
  },
  name: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.semibold,
    color: Colors.text.primary,
  },
  sub: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.secondary,
    marginTop: 2,
  },
  dept: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
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
