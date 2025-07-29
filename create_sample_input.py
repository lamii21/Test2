#!/usr/bin/env python3
"""
Script to create a sample input file for testing the Component Data Processor.

This script generates a realistic input Excel file that simulates data received
from suppliers or collaborators, including various data quality issues.
"""

import pandas as pd
import numpy as np
from datetime import datetime

def create_sample_input():
    """Create a sample input file with test data including data quality issues."""
    
    # Sample data representing various scenarios and data quality issues
    sample_data = [
        # Clean data that exists in Master BOM
        {'PN': 'RES001', 'Project': 'PROJ_A', 'Description': 'Resistor 10K Ohm', 'Supplier': 'SUPPLIER_1', 'Price': 0.06},
        {'PN': 'CAP002', 'Project': 'PROJ_B', 'Description': 'Capacitor 100uF', 'Supplier': 'SUPPLIER_2', 'Price': 0.16},
        {'PN': 'LED004', 'Project': 'PROJ_C', 'Description': 'LED Red 5mm', 'Supplier': 'SUPPLIER_1', 'Price': 0.09},
        
        # Data with whitespace issues (will be cleaned)
        {'PN': '  IC003  ', 'Project': ' PROJ_A ', 'Description': '  Microcontroller ATmega328  ', 'Supplier': ' SUPPLIER_3 ', 'Price': 2.60},
        {'PN': 'SW005\t', 'Project': 'PROJ_B\n', 'Description': 'Push Button Switch', 'Supplier': 'SUPPLIER_4', 'Price': 0.27},
        
        # Data with case issues (will be normalized)
        {'PN': 'old006', 'Project': 'proj_d', 'Description': 'obsolete component', 'Supplier': 'supplier_5', 'Price': 1.10},
        {'PN': 'Act008', 'Project': 'Proj_A', 'Description': 'Active Resistor', 'Supplier': 'Supplier_1', 'Price': 0.11},
        
        # Components that don't exist in Master BOM (will be marked as unknown)
        {'PN': 'NEW001', 'Project': 'PROJ_NEW', 'Description': 'New Component Type A', 'Supplier': 'SUPPLIER_6', 'Price': 1.50},
        {'PN': 'NEW002', 'Project': 'PROJ_A', 'Description': 'New Component Type B', 'Supplier': 'SUPPLIER_7', 'Price': 0.75},
        {'PN': 'UNKNOWN003', 'Project': 'PROJ_X', 'Description': 'Unknown Part', 'Supplier': 'SUPPLIER_8', 'Price': 2.25},
        
        # Data with missing critical values (will be excluded during cleaning)
        {'PN': '', 'Project': 'PROJ_A', 'Description': 'Missing PN', 'Supplier': 'SUPPLIER_1', 'Price': 0.50},
        {'PN': 'MISSING_PROJ', 'Project': '', 'Description': 'Missing Project', 'Supplier': 'SUPPLIER_2', 'Price': 0.30},
        {'PN': None, 'Project': 'PROJ_B', 'Description': 'Null PN', 'Supplier': 'SUPPLIER_3', 'Price': 0.40},
        
        # Valid components with different scenarios
        {'PN': 'CONN011', 'Project': 'PROJ_A', 'Description': 'Connector 2-pin Updated', 'Supplier': 'SUPPLIER_1', 'Price': 0.32},
        {'PN': 'TRANS014', 'Project': 'PROJ_D', 'Description': 'Transistor 2N2222 New', 'Supplier': 'SUPPLIER_4', 'Price': 0.20},
        
        # Components with special characters and formatting issues
        {'PN': 'SPECIAL-001', 'Project': 'PROJ_A', 'Description': 'Component with special chars!@#', 'Supplier': 'SUPPLIER_1', 'Price': 1.00},
        {'PN': 'UNICODE_TEST', 'Project': 'PROJ_B', 'Description': 'Component with unicode: ñáéíóú', 'Supplier': 'SUPPLIER_2', 'Price': 0.85},
        
        # Completely empty row (will be removed during cleaning)
        {'PN': '', 'Project': '', 'Description': '', 'Supplier': '', 'Price': None},
        
        # Row with only some data
        {'PN': 'PARTIAL001', 'Project': 'PROJ_C', 'Description': '', 'Supplier': '', 'Price': None},
        
        # Additional test cases
        {'PN': 'MOTOR017', 'Project': 'PROJ_F', 'Description': 'Servo Motor Updated', 'Supplier': 'SUPPLIER_2', 'Price': 9.00},
        {'PN': 'BUZZER020', 'Project': 'PROJ_I', 'Description': 'Piezo Buzzer New', 'Supplier': 'SUPPLIER_5', 'Price': 1.05},
        
        # Test with extra spaces in multiple places
        {'PN': '  CRYSTAL015  ', 'Project': '  PROJ_A  ', 'Description': '  Crystal   16MHz  ', 'Supplier': '  SUPPLIER_5  ', 'Price': 0.80},
        
        # Test with mixed case and numbers
        {'PN': 'Test123ABC', 'Project': 'proj_Test_01', 'Description': 'Mixed Case Test Component', 'Supplier': 'Test_Supplier', 'Price': 1.25},
    ]
    
    # Create DataFrame
    input_df = pd.DataFrame(sample_data)
    
    # Add some additional columns that might be present in real supplier data
    input_df['Quantity'] = np.random.randint(1, 1000, len(input_df))
    input_df['Lead_Time'] = np.random.choice(['2-3 weeks', '1-2 weeks', '3-4 weeks', 'Stock'], len(input_df))
    input_df['Currency'] = 'USD'
    input_df['Date_Received'] = datetime.now().strftime('%Y-%m-%d')
    
    # Introduce some NaN values in non-critical columns
    input_df.loc[np.random.choice(input_df.index, 3, replace=False), 'Description'] = np.nan
    input_df.loc[np.random.choice(input_df.index, 2, replace=False), 'Supplier'] = np.nan
    
    # Save to Excel file
    output_file = 'Sample_Input_Data.xlsx'
    input_df.to_excel(output_file, index=False, sheet_name='Supplier_Data')
    
    print(f"Sample input file created successfully: {output_file}")
    print(f"Total rows: {len(input_df)}")
    print(f"Rows with missing PN: {input_df['PN'].isna().sum() + (input_df['PN'] == '').sum()}")
    print(f"Rows with missing Project: {input_df['Project'].isna().sum() + (input_df['Project'] == '').sum()}")
    print(f"Rows with missing Description: {input_df['Description'].isna().sum()}")
    
    return input_df

def create_additional_test_files():
    """Create additional test files for edge cases."""
    
    # Create a file with only invalid data
    invalid_data = [
        {'PN': '', 'Project': '', 'Description': '', 'Supplier': '', 'Price': None},
        {'PN': None, 'Project': None, 'Description': None, 'Supplier': None, 'Price': None},
        {'PN': '   ', 'Project': '   ', 'Description': '   ', 'Supplier': '   ', 'Price': None},
    ]
    
    invalid_df = pd.DataFrame(invalid_data)
    invalid_df.to_excel('Sample_Invalid_Data.xlsx', index=False, sheet_name='Invalid_Data')
    
    # Create a file with only new components
    new_components_data = [
        {'PN': 'BRAND_NEW_001', 'Project': 'FUTURE_PROJ', 'Description': 'Future Component A', 'Supplier': 'NEW_SUPPLIER', 'Price': 5.00},
        {'PN': 'BRAND_NEW_002', 'Project': 'FUTURE_PROJ', 'Description': 'Future Component B', 'Supplier': 'NEW_SUPPLIER', 'Price': 3.50},
        {'PN': 'BRAND_NEW_003', 'Project': 'ANOTHER_PROJ', 'Description': 'Another New Component', 'Supplier': 'ANOTHER_SUPPLIER', 'Price': 2.75},
    ]
    
    new_df = pd.DataFrame(new_components_data)
    new_df.to_excel('Sample_New_Components.xlsx', index=False, sheet_name='New_Components')
    
    print("Additional test files created:")
    print("- Sample_Invalid_Data.xlsx (for testing data cleaning)")
    print("- Sample_New_Components.xlsx (for testing unknown component handling)")

if __name__ == "__main__":
    create_sample_input()
    create_additional_test_files()
