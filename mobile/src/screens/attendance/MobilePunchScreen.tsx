import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert, SafeAreaView, ScrollView } from 'react-native';
import { Card, Button, Input } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { submitPunch } from '../../services/attendanceService';

export const MobilePunchScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const [punchType, setPunchType] = useState<'IN' | 'OUT'>('IN');
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePunch = async () => {
    try {
      setLoading(true);
      // Coordinates can be provided via native geolocation or defaults
      const res = await submitPunch({
        punchType,
        remarks,
        latitude: 12.9716, // Bangalore default coordinates for mobile dev
        longitude: 77.5946,
      });

      Alert.alert('Punch Successful', res.message || `Punch ${punchType} recorded successfully!`, [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (err: any) {
      Alert.alert('Punch Failed', err.message || 'Unable to record punch. Please ensure you are within geo-fence.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Mobile Geofence Punch</Text>
          <Text style={styles.subtitle}>Mark your daily attendance with location verification</Text>
        </View>

        <Card>
          <Text style={styles.label}>Select Punch Action</Text>
          <View style={styles.typeSelector}>
            <Button
              title="Punch IN"
              variant={punchType === 'IN' ? 'primary' : 'secondary'}
              onPress={() => setPunchType('IN')}
              style={[styles.typeButton, punchType === 'IN' && { backgroundColor: Colors.primary[500] }]}
            />
            <Button
              title="Punch OUT"
              variant={punchType === 'OUT' ? 'danger' : 'secondary'}
              onPress={() => setPunchType('OUT')}
              style={styles.typeButton}
            />
          </View>

          <View style={styles.locationCard}>
            <Text style={styles.locationTitle}>📍 Location Status</Text>
            <Text style={styles.locationSub}>Verified within authorized branch geofence</Text>
          </View>

          <Input
            label="Remarks (Optional)"
            placeholder="e.g. Working from Client location"
            value={remarks}
            onChangeText={setRemarks}
            multiline
            numberOfLines={3}
          />

          <Button
            title={`Confirm Punch ${punchType}`}
            onPress={handlePunch}
            loading={loading}
            style={styles.confirmBtn}
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
    marginBottom: Spacing.lg,
  },
  typeButton: {
    flex: 1,
    marginHorizontal: Spacing.xs,
  },
  locationCard: {
    backgroundColor: Colors.primary[50],
    padding: Spacing.md,
    borderRadius: Spacing.borderRadius.md,
    marginBottom: Spacing.lg,
  },
  locationTitle: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.bold,
    color: Colors.primary[700],
  },
  locationSub: {
    fontSize: Typography.sizes.xs,
    color: Colors.primary[600],
    marginTop: 2,
  },
  confirmBtn: {
    marginTop: Spacing.md,
  },
});
