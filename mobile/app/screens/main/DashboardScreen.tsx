import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';

export default function DashboardScreen({ navigation }: any) {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const userData = await AsyncStorage.getItem('user');
      if (userData) {
        setUser(JSON.parse(userData));
      }
    } catch (error) {
      console.error('Failed to load user', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await AsyncStorage.removeItem('access_token');
      await AsyncStorage.removeItem('user');
      navigation.replace('Login');
    } catch (error) {
      console.error('Logout failed', error);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <ActivityIndicator size="large" color="#2563eb" />
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>
              Welcome, {user?.first_name || 'User'}! 👋
            </Text>
            <Text style={styles.subtitle}>AI Platform CRM</Text>
          </View>
          <TouchableOpacity
            style={styles.logoutButton}
            onPress={handleLogout}
          >
            <Ionicons name="log-out" size={24} color="#ef4444" />
          </TouchableOpacity>
        </View>

        {/* Quick Stats */}
        <View style={styles.statsContainer}>
          <StatCard icon="👥" label="Contacts" value="0" />
          <StatCard icon="🏢" label="Companies" value="0" />
          <StatCard icon="💼" label="Deals" value="0" />
          <StatCard icon="📞" label="Calls" value="0" />
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <QuickActionButton
            icon="person-add"
            title="New Contact"
            onPress={() => navigation.navigate('Contacts')}
          />
          <QuickActionButton
            icon="call"
            title="View Conversations"
            onPress={() => navigation.navigate('Conversations')}
          />
          <QuickActionButton
            icon="settings"
            title="Settings"
            onPress={() => navigation.navigate('Settings')}
          />
        </View>

        {/* Features */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>CRM Features</Text>
          <FeatureItem
            icon="people"
            title="Manage Contacts"
            description="View and manage all your contacts"
            onPress={() => navigation.navigate('Contacts')}
          />
          <FeatureItem
            icon="business"
            title="Companies"
            description="Track company information"
            onPress={() => navigation.navigate('Companies')}
          />
          <FeatureItem
            icon="briefcase"
            title="Deals"
            description="Manage sales opportunities"
            onPress={() => navigation.navigate('Deals')}
          />
          <FeatureItem
            icon="call"
            title="Conversations"
            description="AI-powered call logs"
            onPress={() => navigation.navigate('Conversations')}
          />
        </View>

        {/* User Info */}
        <View style={styles.userInfoCard}>
          <Text style={styles.userInfoTitle}>Account Info</Text>
          <InfoRow label="Name" value={`${user?.first_name} ${user?.last_name}`} />
          <InfoRow label="Email" value={user?.email} />
          <InfoRow label="Role" value={user?.role} />
          <InfoRow label="Status" value={user?.is_active ? 'Active' : 'Inactive'} />
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function StatCard({ icon, label, value }: any) {
  return (
    <View style={styles.statCard}>
      <Text style={styles.statIcon}>{icon}</Text>
      <Text style={styles.statLabel}>{label}</Text>
      <Text style={styles.statValue}>{value}</Text>
    </View>
  );
}

function QuickActionButton({ icon, title, onPress }: any) {
  return (
    <TouchableOpacity style={styles.quickActionButton} onPress={onPress}>
      <Ionicons name={icon} size={20} color="#2563eb" />
      <Text style={styles.quickActionText}>{title}</Text>
    </TouchableOpacity>
  );
}

function FeatureItem({ icon, title, description, onPress }: any) {
  return (
    <TouchableOpacity style={styles.featureItem} onPress={onPress}>
      <Ionicons name={icon} size={24} color="#2563eb" />
      <View style={styles.featureContent}>
        <Text style={styles.featureTitle}>{title}</Text>
        <Text style={styles.featureDescription}>{description}</Text>
      </View>
      <Ionicons name="chevron-forward" size={20} color="#ccc" />
    </TouchableOpacity>
  );
}

function InfoRow({ label, value }: any) {
  return (
    <View style={styles.infoRow}>
      <Text style={styles.infoLabel}>{label}</Text>
      <Text style={styles.infoValue}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  scrollView: {
    flex: 1,
    padding: 16,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 24,
  },
  greeting: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  logoutButton: {
    padding: 12,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  statCard: {
    width: '48%',
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  statIcon: {
    fontSize: 28,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  statValue: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  quickActionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  quickActionText: {
    marginLeft: 12,
    fontSize: 16,
    fontWeight: '500',
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  featureContent: {
    flex: 1,
    marginLeft: 12,
  },
  featureTitle: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 2,
  },
  featureDescription: {
    fontSize: 12,
    color: '#666',
  },
  userInfoCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 24,
  },
  userInfoTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 12,
  },
  infoRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
  },
  infoLabel: {
    fontSize: 14,
    color: '#666',
  },
  infoValue: {
    fontSize: 14,
    fontWeight: '500',
  },
});
