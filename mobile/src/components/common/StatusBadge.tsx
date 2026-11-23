import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Colors } from '../../theme/colors';
import { Spacing } from '../../theme/spacing';
import { Typography } from '../../theme/typography';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const norm = (status || '').toUpperCase();

  let bg = Colors.neutral[200];
  let text = Colors.neutral[700];

  if (['PRESENT', 'APPROVED', 'PUBLISHED', 'ACTIVE'].includes(norm)) {
    bg = Colors.status.successBg;
    text = Colors.status.success;
  } else if (['ABSENT', 'REJECTED', 'CANCELLED', 'INACTIVE'].includes(norm)) {
    bg = Colors.status.errorBg;
    text = Colors.status.error;
  } else if (['PENDING', 'HALF_DAY', 'DRAFT'].includes(norm)) {
    bg = Colors.status.warningBg;
    text = Colors.status.warning;
  } else if (['WEEKLY_OFF', 'HOLIDAY', 'ON_DUTY'].includes(norm)) {
    bg = Colors.status.infoBg;
    text = Colors.status.info;
  }

  return (
    <View style={[styles.badge, { backgroundColor: bg }]}>
      <Text style={[styles.badgeText, { color: text }]}>{norm.replace(/_/g, ' ')}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  badge: {
    paddingHorizontal: Spacing.sm,
    paddingVertical: 3,
    borderRadius: Spacing.borderRadius.full,
    alignSelf: 'flex-start',
  },
  badgeText: {
    fontSize: Typography.sizes.xs,
    fontWeight: Typography.weights.semibold,
  },
});
