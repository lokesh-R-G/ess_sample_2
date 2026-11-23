import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, RefreshControl, SafeAreaView } from 'react-native';
import { Card } from '../../components/common';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';
import { getNotifications } from '../../services/adminService';
import { AppNotification } from '../../types/common';

export const NotificationsScreen: React.FC = () => {
  const [notifications, setNotifications] = useState<AppNotification[]>([]);
  const [loading, setLoading] = useState(false);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const res = await getNotifications();
      setNotifications(res);
    } catch {
      // Graceful fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const renderItem = ({ item }: { item: AppNotification }) => (
    <Card style={[styles.card, !item.isRead && styles.unreadCard]}>
      <View style={styles.cardHeader}>
        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.time}>{item.createdAt}</Text>
      </View>
      <Text style={styles.message}>{item.message}</Text>
    </Card>
  );

  return (
    <SafeAreaView style={styles.safeArea}>
      <FlatList
        data={notifications}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.container}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadNotifications} colors={[Colors.primary[500]]} />}
        ListHeaderComponent={
          <View style={styles.header}>
            <Text style={styles.screenTitle}>Notifications & Alerts</Text>
          </View>
        }
        ListEmptyComponent={
          !loading ? (
            <Card style={styles.emptyCard}>
              <Text style={styles.emptyText}>No notifications at this time.</Text>
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
  screenTitle: {
    fontSize: Typography.sizes.lg,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  card: {
    marginBottom: Spacing.sm,
  },
  unreadCard: {
    borderColor: Colors.primary[400],
    backgroundColor: Colors.primary[50],
  },
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: Spacing.xs,
  },
  title: {
    fontSize: Typography.sizes.sm,
    fontWeight: Typography.weights.bold,
    color: Colors.text.primary,
  },
  time: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.muted,
  },
  message: {
    fontSize: Typography.sizes.xs,
    color: Colors.text.secondary,
    lineHeight: 18,
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
