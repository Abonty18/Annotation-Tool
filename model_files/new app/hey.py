import chardet

# Read a sample of the file to detect encoding
with open('Thesis Labeled Dataset.csv', 'rb') as f:
    rawdata = f.read(10000)
result = chardet.detect(rawdata)
encoding = result['encoding']
print(f"Detected encoding: {encoding}")
