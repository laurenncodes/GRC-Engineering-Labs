import json

# Function to load bucket data from a JSON file
def load_buckets(path):
    """
    Reads a JSON file containing a list of bucket configurations
    and returns it as a Python list of dictionaries.
    """
    with open(path) as f:
        return json.load(f)

# Function to check whether a bucket has server-side encryption enabled
def check_encryption(bucket):
    """
    Examines the bucket dictionary for the 'ServerSideEncryptionConfiguration' key.
    If that key exists (and is non-null), we consider the bucket encrypted.
    Returns True if encrypted, False otherwise.
    """
    return bucket.get("ServerSideEncryptionConfiguration") is not None

# Main entry point of the script
def main():
    # Load the list of buckets from an input JSON file
    buckets = load_buckets("buckets.json")

    # Open (or create) a CSV file to record encryption status
    with open("encryption_report.csv", "w") as report:
        # Write the header row for the CSV
        report.write("Bucket,Encrypted\n")

        # Iterate over each bucket configuration
        for b in buckets:
            name      = b["Name"]                # Bucket name
            encrypted = check_encryption(b)      # Boolean result of our check

            # Write a line in the CSV: bucket name and True/False
            report.write(f"{name},{encrypted}\n")

            # If the bucket is not encrypted, print a console warning
            # This provides immediate feedback when running the script manually
            if not encrypted:
                print(f"Warning: {name} is not encrypted")

# This conditional ensures that main() only runs when the script is executed directly,
# and not when imported as a module in another script or test suite.
if __name__ == "__main__":
    main()
