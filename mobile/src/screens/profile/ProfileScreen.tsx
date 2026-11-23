import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ScrollView, RefreshControl, SafeAreaView, Alert, TouchableOpacity } from 'react-native';
import { Card, Button, Input } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { useAuth } from '../../store/AuthContext';
import { getProfile, updateProfile } from '../../services/authService';
import { UserProfile } from '../../types/auth';

export const ProfileScreen: React.FC<{ navigation: any }> = ({ navigation }) => {
  const { user, logout, hasPermission } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(user);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'PERSONAL' | 'CONTACT' | 'EMPLOYMENT' | 'BANK'>('PERSONAL');

  // Editable state
  const [mobilePhone, setMobilePhone] = useState('');
  const [addressLine, setAddressLine] = useState('');
  const [city, setCity] = useState('');
  const [saving, setSaving] = useState(false);

  const canAccessAdmin = hasPermission('organization.manage') || hasPermission('employee.read') || hasPermission('leave.approve');

  const loadProfile = async () => {
    try {
      setLoading(true);
      const res = await getProfile();
      setProfile(res);
      setMobilePhone(res.contact?.mobilePhone || '');
      setAddressLine(res.address?.currentAddressLine1 || '');
      setCity(res.address?.currentCity || '');
    } catch {
      // Graceful fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, []);

  const handleSaveContact = async () => {
    try {
      setSaving(true);
      await updateProfile({
        contact: { ...profile?.contact, mobilePhone },
        address: { ...profile?.address, currentAddressLine1: addressLine, currentCity: city },
      });
      Alert.alert('Success', 'Profile updated successfully');
      loadProfile();
    } catch (err: any) {
      Alert.alert('Error', err.message || 'Failed to update profile');
    } finally {
      setSaving(false);
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <ScrollView
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadProfile} colors={[Colors.primary[500]]} />}
      >
        {/* User Summary Card */}
        <Card style={styles.summaryCard}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {profile?.personal?.firstName ? profile.personal.firstName.charAt(0).toUpperCase() : 'U'}
            </Text>
          </View>
          <Text style={styles.profileName}>
            {profile?.personal?.firstName} {profile?.personal?.lastName}
          </Text>
          <Text style={styles.profileCode}>
            {profile?.employeeCode || profile?.empId} • {profile?.employment?.designation || 'Staff'}
          </Text>
        </Card>

        {/* Admin Hub Banner if user has privileges */}
        {canAccessAdmin && (
          <TouchableOpacity
            style={styles.adminBanner}
            onPress={() => navigation.navigate('AdminDashboard')}
          >
            <View>
              <Text style={styles.adminBannerTitle}>🛡️ HRMS Admin Portal</Text>
              <Text style={styles.adminBannerSub}>Access employee directory, approvals & attendance</Text>
            </View>
            <Text style={{ fontSize: 18, color: Colors.primary[700] }}>➔</Text>
          </TouchableOpacity>
        )}

        {/* Tab Selector */}
        <View style={styles.tabBar}>
          {(['PERSONAL', 'CONTACT', 'EMPLOYMENT', 'BANK'] as const).map((tab) => (
            <TouchableOpacity
              key={tab}
              onPress={() => setActiveTab(tab)}
              style={[styles.tabItem, activeTab === tab && styles.activeTabItem]}
            >
              <Text style={[styles.tabText, activeTab === tab && styles.activeTabText]}>{tab}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Tab Content */}
        {activeTab === 'PERSONAL' && (
          <Card>
            <Text style={styles.fieldLabel}>Full Name</Text>
            <Text style={styles.fieldVal}>{profile?.personal?.firstName} {profile?.personal?.lastName || '--'}</Text>

            <Text style={styles.fieldLabel}>Date of Birth</Text>
            <Text style={styles.fieldVal}>{profile?.personal?.dob || '--'}</Text>

            <Text style={styles.fieldLabel}>Gender</Text>
            <Text style={styles.fieldVal}>{profile?.personal?.gender || '--'}</Text>

            <Text style={styles.fieldLabel}>Blood Group</Text>
            <Text style={styles.fieldVal}>{profile?.personal?.bloodGroup || '--'}</Text>
          </Card>
        )}

        {activeTab === 'CONTACT' && (
          <Card>
            <Input
              label="Mobile Number"
              value={mobilePhone}
              onChangeText={setMobilePhone}
              editable={Boolean(profile?.permissions?.canEditMobile ?? true)}
              keyboardType="phone-pad"
            />

            <Input
              label="Work Email"
              value={profile?.contact?.workEmail || ''}
              onChangeText={() => {}}
              editable={false}
            />

            <Input
              label="Current Address"
              value={addressLine}
              onChangeText={setAddressLine}
              editable={Boolean(profile?.permissions?.canEditAddress ?? true)}
            />

            <Input
              label="City"
              value={city}
              onChangeText={setCity}
              editable={Boolean(profile?.permissions?.canEditAddress ?? true)}
            />

            {(profile?.permissions?.canEditMobile || profile?.permissions?.canEditAddress) && (
              <Button
                title="Save Changes"
                onPress={handleSaveContact}
                loading={saving}
                style={{ marginTop: Spacing.sm }}
              />
            )}
          </Card>
        )}

        {activeTab === 'EMPLOYMENT' && (
          <Card>
            <Text style={styles.fieldLabel}>Department</Text>
            <Text style={styles.fieldVal}>{profile?.employment?.department || '--'}</Text>

            <Text style={styles.fieldLabel}>Designation</Text>
            <Text style={styles.fieldVal}>{profile?.employment?.designation || '--'}</Text>

            <Text style={styles.fieldLabel}>Date of Joining</Text>
            <Text style={styles.fieldVal}>{profile?.employment?.dateOfJoining || '--'}</Text>

            <Text style={styles.fieldLabel}>Reporting Manager</Text>
            <Text style={styles.fieldVal}>{profile?.employment?.reportingManager || '--'}</Text>
          </Card>
        )}

        {activeTab === 'BANK' && (
          <Card>
            <Text style={styles.fieldLabel}>Bank Name</Text>
            <Text style={styles.fieldVal}>{profile?.bank?.bankName || '--'}</Text>

            <Text style={styles.fieldLabel}>Account Number</Text>
            <Text style={styles.fieldVal}>
              {profile?.bank?.accountNumber ? `•••• ${profile.bank.accountNumber.slice(-4)}` : '--'}
            </Text>

            <Text style={styles.fieldLabel}>IFSC Code</Text>
            <Text style={styles.fieldVal}>{profile?.bank?.ifscCode || '--'}</Text>
          </Card>
        )}

        {/* Logout */}
        <Button
          title="Sign Out"
          variant="danger"
          onPress={logout}
          style={styles.logoutBtn}
        />
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
  summaryCard: {
    alignItems: 'center',
    paddingVertical: Spacing.xl,
  },
  avatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: Colors.primary[500],
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: Spacing.sm,
  },
  avatarText: {
    color: Colors.neutral.white,
    fontSize: Typography.sizes.title,
    fontWeight: Typography.weights.bold,
  },
  profileName: {
    fontSize: Typography.sizes.lg,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  profileCode: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: 2,
  },
  adminBanner: {
    backgroundColor: Colors.primary[50],
    borderColor: Colors.primary[200],
    borderWidth: 1,
    borderRadius: Spacing.borderRadius.md,
    padding: Spacing.md,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.md,
  },
  adminBannerTitle: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.bold,
    color: Colors.primary[700],
  },
  adminBannerSub: {
    fontSize: Typography.sizes.xs,
    color: Colors.primary[600],
    marginTop: 2,
  },
  tabBar: {
    flexDirection: 'row',
    backgroundColor: Colors.neutral[200],
    borderRadius: Spacing.borderRadius.md,
    padding: 3,
    marginBottom: Spacing.md,
  },
  tabItem: {
    flex: 1,
    alignItems: 'center',
    paddingVertical: Spacing.sm,
    borderRadius: Spacing.borderRadius.sm,
  },
  activeTabItem: {
    backgroundColor: Colors.neutral.white,
  },
  tabText: {
    fontSize: 10,
    fontWeight: Typography.weights.bold,
    color: Colors.text.muted,
  },
  activeTabText: {
    color: Colors.primary[500],
  },
  fieldLabel: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
    marginTop: Spacing.xs,
  },
  fieldVal: {
    fontSize: Typography.sizes.base,
    fontWeight: Typography.weights.medium,
    color: Colors.text.primary,
    marginBottom: Spacing.sm,
  },
  logoutBtn: {
    marginTop: Spacing.lg,
    marginBottom: Spacing.xl,
  },
});
