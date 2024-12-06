import math

import pandas as pd
from lightphe import Paillier
from pandas.core.dtypes.inference import is_number, is_float

# Initialize Paillier cryptosystem
cs = Paillier()

# Define the scaling factor (e.g., for 3 decimal places, use 1000)
SCALING_FACTOR = 1000

# Load the Excel file with financial data
file_path = "Financial_Data.xlsx"  # Change this to your Excel file path
df = pd.read_excel(file_path)

# Function to encrypt all values in the DataFrame
def encrypt_column(df, cs, scaling_factor):
    encrypted_df = df.copy()  # Create a copy of the dataframe to hold encrypted data
    for column in df.columns:
        encrypted_values = []
        for value in df[column]:
            if is_number(value) or is_float(value):  # Check if the value is numerical
                # Scale the float to integer
                scaled_value = int(value * scaling_factor)
                encrypted_value = cs.encrypt(scaled_value)
                encrypted_values.append(encrypted_value)
            else:
                encrypted_values.append(value)  # Leave non-numerical values as is
        encrypted_df[column] = encrypted_values  # Replace the original column with encrypted values
    return encrypted_df

# Encrypt the data
encrypted_df = encrypt_column(df, cs, SCALING_FACTOR)

# Save the encrypted data to a new Excel file
encrypted_file_path = "encrypted_financial_data.xlsx"
encrypted_df.to_excel(encrypted_file_path, index=False)

print(f"Encrypted data saved to {encrypted_file_path}")

# Decrypting and rescaling a specific value for demonstration
def decrypt_and_rescale(encrypted_value, cs, scaling_factor):
    decrypted_value = cs.decrypt(encrypted_value)
    return decrypted_value / scaling_factor  # Rescale to float

# Example: Decrypting the first encrypted value from a column (e.g., 'Amount')
decrypted_value = decrypt_and_rescale(encrypted_df['Encrypted_Amount'][0], cs, SCALING_FACTOR)
print(f"Decrypted value: {decrypted_value}")
