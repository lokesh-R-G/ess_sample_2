import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, SafeAreaView, TouchableOpacity, Alert } from 'react-native';
import { Card, Button, Input, StatusBadge } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { getMyReimbursements, submitReimbursement } from '../../services/adminService';
import { ReimbursementClaim } from '../../types/common';

export const ReimbursementsScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [claims, setClaims] = useState<ReimbursementClaim[]>([]);
  const [loading, setLoading] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);

  // Form state
  const [category, setCategory] = useState('Travel');
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [description, setDescription] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const loadClaims = async () => {
    try {
      setLoading(true);
      const res = await getMyReimbursements();
      setClaims(res);
    } catch {
      // Error handling
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadClaims();
  }, []);

  const handleCreateClaim = async () => {
    if (!title.trim() || !amount.trim()) {
      Alert.alert('Validation Error', 'Please enter a title and valid claim amount');
      return;
    }

    try {
      setSubmitting(true);
      await submitReimbursement({
        category,
        title: title.trim(),
        amount: parseFloat(amount),
        description: description.trim(),
      });
      Alert.alert('Claim Submitted', 'Your expense claim has been submitted for approval.');
      setShowAddModal(false);
      setTitle('');
      setAmount('');
      setDescription('');
      loadClaims();
    } catch (err: any) {
      Alert.alert('Submission Error', err.message || 'Failed to submit claim');
    } finally {
      setSubmitting(false);
    }
  };

  const renderClaim = ({ item }: { item: ReimbursementClaim }) => (
    <Card style={styles.claimCard}>
      <View style={styles.claimHeader}>
        <View>
          <Text style={styles.claimTitle}>{item.title}</Text>
          <Text style={styles.claimCategory}>{item.category} • {item.claimDate}</Text>
        </View>
        <StatusBadge status={item.status} />
      </View>
      <View style={styles.claimBody}>
        <Text style={styles.amountLabel}>Claim Amount</Text>
        <Text style={styles.amountVal}>₹{item.amount.toLocaleString('en-IN')}</Text>
      </View>
      {Boolean(item.description) && (
        <Text style={styles.descText} numberOfLines={2}>{item.description}</Text>
      )}
    </Card>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={claims}
        keyExtractor={(item) => item.id}
        renderItem={renderClaim}
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadClaims} colors={[Colors.primary[500]]} />}
        ListHeaderComponent={
          <View>
            <View style={styles.header}>
              <Text style={styles.title}>Expense Claims</Text>
              <Button
                title={showAddModal ? "Cancel" : "+ New Claim"}
                variant={showAddModal ? "outline" : "primary"}
                onPress={() => setShowAddModal(!showAddModal)}
                style={{ height: 38 }}
              />
            </View>

            {showAddModal && (
              <Card style={styles.modalCard}>
                <Text style={styles.formTitle}>Submit Expense Claim</Text>
                <Input
                  label="Claim Title"
                  placeholder="e.g. Client Dinner / Cab Fare"
                  value={title}
                  onChangeText={setTitle}
                />
                <Input
                  label="Amount (₹)"
                  placeholder="e.g. 1500"
                  value={amount}
                  onChangeText={setAmount}
                  keyboardType="numeric"
                />
                <Input
                  label="Description / Purpose"
                  placeholder="Details regarding this expense"
                  value={description}
                  onChangeText={setDescription}
                  multiline
                  numberOfLines={3}
                />
                <Button
                  title="Submit Claim"
                  onPress={handleCreateClaim}
                  loading={submitting}
                  style={{ marginTop: Spacing.sm }}
                />
              </Card>
            )}
          </View>
        }
        ListEmptyComponent={
          !loading ? (
            <Card style={styles.emptyCard}>
              <Text style={styles.emptyText}>No reimbursement claims filed yet.</Text>
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
  modalCard: {
    backgroundColor: Colors.neutral[50],
    borderColor: Colors.primary[300],
    borderWidth: 1,
    marginBottom: Spacing.lg,
  },
  formTitle: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
    marginBottom: Spacing.sm,
  },
  claimCard: {
    marginBottom: Spacing.sm,
  },
  claimHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  claimTitle: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.semibold,
    color: Colors.text.primary,
  },
  claimCategory: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: 2,
  },
  claimBody: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: Spacing.xs,
  },
  amountLabel: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.secondary,
  },
  amountVal: {
    fontSize: Typography.sizes.md,
    fontWeight: Typography.weights.bold,
    color: Colors.primary[600],
  },
  descText: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
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
