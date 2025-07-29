#!/usr/bin/env python3
"""
Script to create a sample Master BOM file for testing the Component Data Processor.

This script generates a realistic Master BOM Excel file with various component statuses
to demonstrate all the processing scenarios.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def create_sample_master_bom():
    """Create a sample Master BOM file with test data."""
    
    # Sample data representing different scenarios
    sample_data = [
        # Components with Status 'D' (Deprecated) - will be updated to 'X'
        {'PN': 'RES001', 'Project': 'PROJ_A', 'Description': 'Resistor 10K Ohm', 'Supplier': 'SUPPLIER_1', 'Price': 0.05, 'Status': 'D'},
        {'PN': 'CAP002', 'Project': 'PROJ_B', 'Description': 'Capacitor 100uF', 'Supplier': 'SUPPLIER_2', 'Price': 0.15, 'Status': 'D'},
        {'PN': 'IC003', 'Project': 'PROJ_A', 'Description': 'Microcontroller ATmega328', 'Supplier': 'SUPPLIER_3', 'Price': 2.50, 'Status': 'D'},
        
        # Components with Status '0' (Duplicate/Uncertain) - will create duplicate rows
        {'PN': 'LED004', 'Project': 'PROJ_C', 'Description': 'LED Red 5mm', 'Supplier': 'SUPPLIER_1', 'Price': 0.08, 'Status': '0'},
        {'PN': 'SW005', 'Project': 'PROJ_B', 'Description': 'Push Button Switch', 'Supplier': 'SUPPLIER_4', 'Price': 0.25, 'Status': '0'},
        
        # Components with Status 'X' (Already Old) - will be skipped
        {'PN': 'OLD006', 'Project': 'PROJ_D', 'Description': 'Obsolete Component', 'Supplier': 'SUPPLIER_5', 'Price': 1.00, 'Status': 'X'},
        {'PN': 'OLD007', 'Project': 'PROJ_A', 'Description': 'Legacy IC', 'Supplier': 'SUPPLIER_2', 'Price': 5.00, 'Status': 'X'},
        
        # Components with valid status (Active components)
        {'PN': 'ACT008', 'Project': 'PROJ_A', 'Description': 'Active Resistor', 'Supplier': 'SUPPLIER_1', 'Price': 0.10, 'Status': 'A'},
        {'PN': 'ACT009', 'Project': 'PROJ_B', 'Description': 'Active Capacitor', 'Supplier': 'SUPPLIER_3', 'Price': 0.20, 'Status': 'A'},
        {'PN': 'ACT010', 'Project': 'PROJ_C', 'Description': 'Active IC', 'Supplier': 'SUPPLIER_4', 'Price': 3.00, 'Status': 'A'},
        
        # Additional components for comprehensive testing
        {'PN': 'CONN011', 'Project': 'PROJ_A', 'Description': 'Connector 2-pin', 'Supplier': 'SUPPLIER_1', 'Price': 0.30, 'Status': 'A'},
        {'PN': 'CONN012', 'Project': 'PROJ_B', 'Description': 'Connector 4-pin', 'Supplier': 'SUPPLIER_2', 'Price': 0.45, 'Status': 'D'},
        {'PN': 'DIODE013', 'Project': 'PROJ_C', 'Description': 'Diode 1N4007', 'Supplier': 'SUPPLIER_3', 'Price': 0.12, 'Status': 'A'},
        {'PN': 'TRANS014', 'Project': 'PROJ_D', 'Description': 'Transistor 2N2222', 'Supplier': 'SUPPLIER_4', 'Price': 0.18, 'Status': '0'},
        {'PN': 'CRYSTAL015', 'Project': 'PROJ_A', 'Description': 'Crystal 16MHz', 'Supplier': 'SUPPLIER_5', 'Price': 0.75, 'Status': 'A'},
        
        # Components with different projects
        {'PN': 'SENSOR016', 'Project': 'PROJ_E', 'Description': 'Temperature Sensor', 'Supplier': 'SUPPLIER_1', 'Price': 1.25, 'Status': 'A'},
        {'PN': 'MOTOR017', 'Project': 'PROJ_F', 'Description': 'Servo Motor', 'Supplier': 'SUPPLIER_2', 'Price': 8.50, 'Status': 'D'},
        {'PN': 'BATTERY018', 'Project': 'PROJ_G', 'Description': 'Li-ion Battery', 'Supplier': 'SUPPLIER_3', 'Price': 12.00, 'Status': 'A'},
        {'PN': 'DISPLAY019', 'Project': 'PROJ_H', 'Description': 'LCD Display 16x2', 'Supplier': 'SUPPLIER_4', 'Price': 4.50, 'Status': 'X'},
        {'PN': 'BUZZER020', 'Project': 'PROJ_I', 'Description': 'Piezo Buzzer', 'Supplier': 'SUPPLIER_5', 'Price': 0.95, 'Status': '0'},
    ]
    
    # Create DataFrame
    master_bom_df = pd.DataFrame(sample_data)
    
    # Add additional metadata columns
    master_bom_df['Last_Updated'] = datetime.now().strftime('%Y-%m-%d')
    master_bom_df['Category'] = master_bom_df['Description'].apply(categorize_component)
    master_bom_df['Lead_Time_Days'] = np.random.randint(1, 30, len(master_bom_df))
    master_bom_df['Min_Order_Qty'] = np.random.choice([1, 10, 100, 1000], len(master_bom_df))
    
    # Save to Excel file
    output_file = 'Master_BOM.xlsx'
    master_bom_df.to_excel(output_file, index=False, sheet_name='Master_BOM')
    
    print(f"Sample Master BOM created successfully: {output_file}")
    print(f"Total components: {len(master_bom_df)}")
    print("\nStatus distribution:")
    print(master_bom_df['Status'].value_counts())
    
    return master_bom_df

def categorize_component(description):
    """Categorize components based on description."""
    description_lower = description.lower()
    
    if any(word in description_lower for word in ['resistor', 'resistance']):
        return 'Passive - Resistor'
    elif any(word in description_lower for word in ['capacitor', 'cap']):
        return 'Passive - Capacitor'
    elif any(word in description_lower for word in ['led', 'light']):
        return 'Optoelectronics'
    elif any(word in description_lower for word in ['ic', 'microcontroller', 'processor']):
        return 'Integrated Circuit'
    elif any(word in description_lower for word in ['connector', 'conn']):
        return 'Connector'
    elif any(word in description_lower for word in ['switch', 'button']):
        return 'Electromechanical'
    elif any(word in description_lower for word in ['diode']):
        return 'Semiconductor'
    elif any(word in description_lower for word in ['transistor', 'trans']):
        return 'Semiconductor'
    elif any(word in description_lower for word in ['crystal', 'oscillator']):
        return 'Frequency Control'
    elif any(word in description_lower for word in ['sensor']):
        return 'Sensor'
    elif any(word in description_lower for word in ['motor']):
        return 'Electromechanical'
    elif any(word in description_lower for word in ['battery']):
        return 'Power Supply'
    elif any(word in description_lower for word in ['display', 'lcd']):
        return 'Display'
    elif any(word in description_lower for word in ['buzzer', 'speaker']):
        return 'Audio'
    else:
        return 'Other'

if __name__ == "__main__":
    create_sample_master_bom()
