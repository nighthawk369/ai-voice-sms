import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ActivityIndicator,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';

interface BusinessType {
  value: string;
  label: string;
  category: string;
  description: string;
}

interface BusinessTypeSelectorProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export default function BusinessTypeSelector({
  value,
  onChange,
  disabled = false,
}: BusinessTypeSelectorProps) {
  const [businessTypes, setBusinessTypes] = useState<BusinessType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchBusinessTypes();
  }, []);

  const fetchBusinessTypes = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/business-types');
      const data = await response.json();
      setBusinessTypes(data.business_types);
    } catch (error) {
      console.error('Error fetching business types:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectedBT = businessTypes.find((bt) => bt.value === value);

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#3b82f6" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.label}>
        Business Type<Text style={styles.required}>*</Text>
      </Text>

      <View style={styles.pickerContainer}>
        <Picker
          selectedValue={value}
          onValueChange={onChange}
          enabled={!disabled}
          style={styles.picker}
          itemStyle={styles.pickerItem}
        >
          <Picker.Item label="-- Select your business type --" value="" />

          {businessTypes.map((bt) => (
            <Picker.Item key={bt.value} label={bt.label} value={bt.value} />
          ))}
        </Picker>
      </View>

      {selectedBT && (
        <View style={styles.descriptionContainer}>
          <Text style={styles.descriptionTitle}>{selectedBT.label}</Text>
          <Text style={styles.descriptionText}>{selectedBT.description}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 12,
  },

  label: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    color: '#1f2937',
  },

  required: {
    color: '#ef4444',
    marginLeft: 4,
  },

  pickerContainer: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 6,
    overflow: 'hidden',
    backgroundColor: '#ffffff',
  },

  picker: {
    height: 50,
    width: '100%',
  },

  pickerItem: {
    fontSize: 14,
    height: 50,
  },

  descriptionContainer: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#eff6ff',
    borderRadius: 6,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },

  descriptionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1e40af',
    marginBottom: 4,
  },

  descriptionText: {
    fontSize: 12,
    color: '#1e40af',
    lineHeight: 16,
  },
});
