import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Ionicons } from '@expo/vector-icons';

// Auth Screens
import LoginScreen from '../screens/auth/LoginScreen';
import SignupScreen from '../screens/auth/SignupScreen';

// Main Screens
import DashboardScreen from '../screens/main/DashboardScreen';
import ContactsScreen from '../screens/crm/ContactsScreen';
import ContactDetailScreen from '../screens/crm/ContactDetailScreen';
import CompaniesScreen from '../screens/crm/CompaniesScreen';
import DealsScreen from '../screens/crm/DealsScreen';
import ActivitiesScreen from '../screens/crm/ActivitiesScreen';
import ConversationsScreen from '../screens/voice/ConversationsScreen';
import SettingsScreen from '../screens/settings/SettingsScreen';

const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

function AuthNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
      }}
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Signup" component={SignupScreen} />
    </Stack.Navigator>
  );
}

function CRMNavigator() {
  return (
    <Stack.Navigator>
      <Stack.Screen
        name="ContactsList"
        component={ContactsScreen}
        options={{ title: 'Contacts' }}
      />
      <Stack.Screen
        name="ContactDetail"
        component={ContactDetailScreen}
        options={{ title: 'Contact Details' }}
      />
    </Stack.Navigator>
  );
}

function MainNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: any = 'home';
          if (route.name === 'Dashboard') iconName = 'home';
          else if (route.name === 'Contacts') iconName = 'people';
          else if (route.name === 'Companies') iconName = 'business';
          else if (route.name === 'Deals') iconName = 'briefcase';
          else if (route.name === 'Conversations') iconName = 'call';
          else if (route.name === 'Settings') iconName = 'settings';

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#2563eb',
        tabBarInactiveTintColor: '#999',
        headerShown: true,
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardScreen}
        options={{ title: 'Dashboard' }}
      />
      <Tab.Screen
        name="Contacts"
        component={CRMNavigator}
        options={{ title: 'Contacts' }}
      />
      <Tab.Screen
        name="Companies"
        component={CompaniesScreen}
        options={{ title: 'Companies' }}
      />
      <Tab.Screen
        name="Deals"
        component={DealsScreen}
        options={{ title: 'Deals' }}
      />
      <Tab.Screen
        name="Conversations"
        component={ConversationsScreen}
        options={{ title: 'Calls' }}
      />
      <Tab.Screen
        name="Settings"
        component={SettingsScreen}
        options={{ title: 'Settings' }}
      />
    </Tab.Navigator>
  );
}

export default function RootNavigator() {
  const [isLoading, setIsLoading] = useState(true);
  const [userToken, setUserToken] = useState<string | null>(null);

  useEffect(() => {
    const bootstrapAsync = async () => {
      try {
        const token = await AsyncStorage.getItem('access_token');
        setUserToken(token);
      } catch (e) {
        console.error('Failed to restore token', e);
      }
      setIsLoading(false);
    };

    bootstrapAsync();
  }, []);

  if (isLoading) {
    return null; // Show splash screen here
  }

  return (
    <NavigationContainer>
      {userToken ? <MainNavigator /> : <AuthNavigator />}
    </NavigationContainer>
  );
}
