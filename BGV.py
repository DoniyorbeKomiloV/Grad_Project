import pandas as pd
import seal as ps

# Step 1: Load the Excel file
file_path = "Financial_Data.xlsx"  # Replace with your Excel file
data = pd.read_excel(file_path)

print("Original Data:")
print(data.head())  # Print the first few rows for verification

# Step 2: Set up SEAL context for BGV encryption
def setup_context():
    params = ps.EncryptionParameters(ps.SCHEME_TYPE.BGV)
    params.set_poly_modulus_degree(8192)  # Polynomial degree
    params.set_coeff_modulus(ps.CoeffModulus.BFVDefault(8192))  # Coeff modulus
    params.set_plain_modulus(256)  # Plaintext modulus (suitable for integers)
    context = ps.SEALContext.Create(params)
    return context

context = setup_context()

# Step 3: Key generation
keygen = ps.KeyGenerator(context)
secret_key = keygen.secret_key()
public_key = keygen.public_key()
encryptor = ps.Encryptor(context, public_key)
decryptor = ps.Decryptor(context, secret_key)
evaluator = ps.Evaluator(context)
encoder = ps.BatchEncoder(context)

# Step 4: Encrypt the data
def encrypt_column(column):
    """Encrypt a column of data."""
    encrypted_column = []
    for value in column:
        plain = encoder.encode([int(value)] * encoder.slot_count())  # Encode value
        encrypted = ps.Ciphertext()
        encryptor.encrypt(plain, encrypted)  # Encrypt encoded value
        encrypted_column.append(encrypted)
    return encrypted_column

# Encrypt numerical columns in the Excel data
encrypted_data = {}
for col in data.select_dtypes(include=["number"]).columns:
    print(f"Encrypting column: {col}")
    encrypted_data[col] = encrypt_column(data[col])

# Step 5: Perform encrypted computations (e.g., add interest)
def add_interest(encrypted_column, rate):
    """Add interest to an encrypted column."""
    interest_plain = encoder.encode([int(rate * 100)] * encoder.slot_count())
    encrypted_result = []
    for encrypted_value in encrypted_column:
        result = ps.Ciphertext()
        evaluator.add_plain(encrypted_value, interest_plain, result)
        encrypted_result.append(result)
    return encrypted_result

# Example: Add 5% interest to a column (e.g., "Balance")
if "Balance" in encrypted_data:
    print("Adding 5% interest to 'Balance' column...")
    encrypted_data["Balance"] = add_interest(encrypted_data["Balance"], 0.05)

# Step 6: Decrypt the data
def decrypt_column(encrypted_column):
    """Decrypt a column of encrypted data."""
    decrypted_column = []
    for encrypted_value in encrypted_column:
        plain = ps.Plaintext()
        decryptor.decrypt(encrypted_value, plain)  # Decrypt ciphertext
        decoded = encoder.decode(plain)  # Decode plaintext
        decrypted_column.append(decoded[0])  # Extract the first slot
    return decrypted_column

# Decrypt and save the results
decrypted_data = {}
for col, encrypted_col in encrypted_data.items():
    print(f"Decrypting column: {col}")
    decrypted_data[col] = decrypt_column(encrypted_col)

# Save decrypted data to a new Excel file
decrypted_df = pd.DataFrame(decrypted_data)
decrypted_df.to_excel("BGV_decrypted_Financial_Data.xlsx", index=False)
print("Decrypted data saved to 'BGV_decrypted_Financial_Data.xlsx'")
