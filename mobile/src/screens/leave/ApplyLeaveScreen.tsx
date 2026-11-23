import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert, SafeAreaView, ScrollView } from 'react-native';
import { Card, Button, Input } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { createLeaveRequest } from '../../services/leaveService';

export const ApplyLeaveScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [leaveTypeId, setLeaveTypeId] = useState('CASUAL');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);

  const handleApply = async () => {
    if (!startDate || !endDate) {
      Alert.alert('Validation Error', 'Please specify both Start Date and End Date (YYYY-MM-DD)');
      return;
    }
    if (!reason.trim()) {
      Alert.alert('Validation Error', 'Please enter a reason for the leave');
      return;
    }

    try {
      setLoading(true);
      await createLeaveRequest({
        leaveTypeId,
        startDate: startDate.trim(),
        endDate: endDate.trim(),
        reason: reason.trim(),
      });
      Alert.alert('Success', 'Leave application submitted successfully!', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (err: any) {
      Alert.alert('Submission Error', err.message || 'Failed to submit leave request');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Apply for Leave</Text>
          <Text style={styles.subtitle}>Submit request for supervisor review</Text>
        </View>

        <Card>
          <Text style={styles.label}>Leave Type</Text>
          <View style={styles.typeSelector}>
            {['CASUAL', 'SICK', 'EARNED'].map((type) => (
              <Button
                key={type}
                title={type}
                variant={leaveTypeId === type ? 'primary' : 'secondary'}
                onPress={() => setLeaveTypeId(type)}
                style={[
                  styles.typeBtn,
                  leaveTypeId === type && { backgroundColor: Colors.primary[500] }
                ]}
              />
            ))}
          </View>

          <Input
            label="Start Date (YYYY-MM-DD)"
            placeholder="2026-12-01"
            value={startDate}
            onChangeText={setStartDate}
          />

          <Input
            label="End Date (YYYY-MM-DD)"
            placeholder="2026-12-02"
            value={endDate}
            onChangeText={setEndDate}
          />

          <Input
            label="Reason for Leave"
            placeholder="Provide context or explanation"
            value={reason}
            onChangeText={setReason}
            multiline
            numberOfLines={4}
          />

          <Button
            title="Submit Application"
            onPress={handleApply}
            loading={loading}
            style={styles.submitBtn}
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
  label: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.medium,
    color: Colors.text.secondary,
    marginBottom: Spacing.xs,
  },
  typeSelector: {
    flexDirection: 'row',
    marginBottom: Spacing.md,
  },
  typeBtn: {
    flex: 1,
    marginHorizontal: 3,
  },
  submitBtn: {
    marginTop: Spacing.md,
  },
});
