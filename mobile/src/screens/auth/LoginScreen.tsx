import React, { useState } from 'react';
import { View, Text, StyleSheet, Alert, ScrollView, SafeAreaView, KeyboardAvoidingView, Platform } from 'react-native';
import { useAuth } from '../../store/AuthContext';
import { Input, Button, Card } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';

export const LoginScreen: React.FC = () => {
  const { login } = useAuth();
  const [empId, setEmpId] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    if (!empId.trim()) {
      setError('Please enter your Employee ID');
      return;
    }
    if (!password) {
      setError('Please enter your password');
      return;
    }

    try {
      setLoading(true);
      setError('');
      await login(empId.trim(), password);
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
      Alert.alert('Login Error', err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.keyboardContainer}>
        <ScrollView contentContainerStyle={styles.scrollContent}>
          <View style={styles.header}>
            <View style={styles.logoBadge}>
              <Text style={styles.logoText}>IDS</Text>
            </View>
            <Text style={styles.title}>ESS / HRMS Portal</Text>
            <Text style={styles.subtitle}>Sign in with your employee credentials</Text>
          </View>

          <Card style={styles.card}>
            {Boolean(error) && (
              <View style={styles.errorBanner}>
                <Text style={styles.errorBannerText}>{error}</Text>
              </View>
            )}

            <Input
              label="Employee ID"
              placeholder="e.g. EMP001"
              value={empId}
              onChangeText={(text) => {
                setEmpId(text);
                setError('');
              }}
              autoCapitalize="characters"
            />

            <Input
              label="Password"
              placeholder="Enter your password"
              value={password}
              onChangeText={(text) => {
                setPassword(text);
                setError('');
              }}
              secureTextEntry
            />

            <Button
              title="Sign In"
              onPress={handleLogin}
              loading={loading}
              style={styles.loginButton}
            />
          </Card>

          <Text style={styles.footerText}>
            Protected by IDS Role-Based Access Control
          </Text>
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: Colors.background.light,
  },
  keyboardContainer: {
    flex: 1,
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: Spacing.screenPadding,
  },
  header: {
    alignItems: 'center',
    marginBottom: Spacing.xxl,
  },
  logoBadge: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: Colors.primary[500],
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.md,
  },
  logoText: {
    color: Colors.neutral.white,
    fontSize: Typography.sizes.xxl,
    fontWeight: Typography.weights.bold,
  },
  title: {
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  subtitle: {
    fontSize: Typography.sizes.base,
    color: Colors.text.secondary,
    marginTop: Spacing.xs,
  },
  card: {
    padding: Spacing.xl,
  },
  loginButton: {
    marginTop: Spacing.sm,
  },
  errorBanner: {
    backgroundColor: Colors.status.errorBg,
    padding: Spacing.md,
    borderRadius: Spacing.borderRadius.md,
    marginBottom: Spacing.md,
  },
  errorBannerText: {
    color: Colors.status.error,
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.medium,
  },
  footerText: {
    textAlign: 'center',
    color: Colors.text.muted,
    fontSize: Typography.sizes.xs,
    marginTop: Spacing.xl,
  },
});
