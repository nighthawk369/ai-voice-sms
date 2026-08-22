/**
 * Contacts Screen - React Native/Expo
 */

import React, { useState } from 'react';
import {
  View,
  Text,
  FlatList,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  TextInput,
  Alert,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { api } from '../../lib/api';

interface Contact {
  id: string;
  first_name: string;
  last_name: string;
  email?: string;
  phone: string;
  contact_type: string;
  status: string;
  created_at: string;
}

export default function ContactsScreen() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [error, setError] = useState<string | null>(null);

  useFocusEffect(
    React.useCallback(() => {
      loadContacts();
    }, [search])
  );

  const loadContacts = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.searchContacts(search, undefined, undefined, 0, 100);
      setContacts(response.items);
    } catch (err: any) {
      setError(err.message || 'Failed to load contacts');
      Alert.alert('Error', 'Failed to load contacts');
    } finally {
      setLoading(false);
    }
  };

  const renderContactItem = ({ item }: { item: Contact }) => (
    <TouchableOpacity style={styles.contactCard} onPress={() => {/* Navigate to detail */}}>
      <View style={styles.contactHeader}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {item.first_name.charAt(0)}
            {item.last_name.charAt(0)}
          </Text>
        </View>
        <View style={styles.contactInfo}>
          <Text style={styles.contactName}>
            {item.first_name} {item.last_name}
          </Text>
          <Text style={styles.contactPhone}>{item.phone}</Text>
          {item.email && <Text style={styles.contactEmail}>{item.email}</Text>}
        </View>
      </View>
      <View style={styles.contactMeta}>
        <View style={[styles.badge, getBadgeColor(item.contact_type)]}>
          <Text style={styles.badgeText}>{item.contact_type}</Text>
        </View>
        <View style={[styles.badge, getStatusColor(item.status)]}>
          <Text style={styles.badgeText}>{item.status}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  const getBadgeColor = (type: string) => {
    const colors: any = {
      LEAD: { backgroundColor: '#FEE2E2' },
      PROSPECT: { backgroundColor: '#DBEAFE' },
      CUSTOMER: { backgroundColor: '#DCFCE7' },
    };
    return colors[type] || { backgroundColor: '#F3F4F6' };
  };

  const getStatusColor = (status: string) => {
    const colors: any = {
      ACTIVE: { backgroundColor: '#DCFCE7' },
      INACTIVE: { backgroundColor: '#FEE2E2' },
    };
    return colors[status] || { backgroundColor: '#F3F4F6' };
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Contacts</Text>
        <TouchableOpacity style={styles.addButton}>
          <Text style={styles.addButtonText}>+ Add</Text>
        </TouchableOpacity>
      </View>

      <TextInput
        style={styles.searchInput}
        placeholder="Search contacts..."
        value={search}
        onChangeText={setSearch}
        placeholderTextColor="#9CA3AF"
      />

      {loading ? (
        <View style={styles.loaderContainer}>
          <ActivityIndicator size="large" color="#2563EB" />
        </View>
      ) : error ? (
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadContacts}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={contacts}
          renderItem={renderContactItem}
          keyExtractor={(item) => item.id}
          onEndReachedThreshold={0.5}
          scrollEnabled
          contentContainerStyle={styles.listContent}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#111827',
  },
  addButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#2563EB',
    borderRadius: 6,
  },
  addButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  searchInput: {
    marginHorizontal: 16,
    marginVertical: 12,
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRadius: 8,
    fontSize: 14,
  },
  listContent: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  contactCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    marginBottom: 12,
    padding: 12,
  },
  contactHeader: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  avatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#2563EB',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  avatarText: {
    color: '#FFFFFF',
    fontWeight: '600',
    fontSize: 14,
  },
  contactInfo: {
    flex: 1,
  },
  contactName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  contactPhone: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  contactEmail: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 2,
  },
  contactMeta: {
    flexDirection: 'row',
    gap: 8,
  },
  badge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
  },
  badgeText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#374151',
  },
  loaderContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 16,
  },
  errorText: {
    color: '#DC2626',
    fontSize: 14,
    marginBottom: 12,
  },
  retryButton: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: '#2563EB',
    borderRadius: 6,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
});
