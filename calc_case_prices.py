import json
with open('cardinal.json', 'r') as f:
    data = json.load(f)

# Calculate case prices for each size
print('PC61 in Cardinal - Case Pricing:')
print('-------------------------------')
print(f\
Sale
period:
data['meta']['sale_start_date']
to
data['meta']['sale_end_date']
\\n\)

# Calculate and display pricing for each size
for size in sorted(data['original_price'].keys()):
    case_size = data['case_size'][size]
    orig_price = data['original_price'][size]
    sale_price = data['sale_price'][size]
    program_price = data['program_price'][size]
    
    total_case_orig = orig_price * case_size
    total_case_sale = sale_price * case_size
    total_case_program = program_price * case_size
    
    print(f'Size {size}:')
    print(f'  Case Size: {case_size} units')
    print(f'  Per-Unit Price: ')
    print(f'  Per-Unit Sale Price: ')
    print(f'  Per-Unit Program Price: ')
    print(f'  Total Case Price: ')
    print(f'  Total Case Sale Price: ')
    print(f'  Total Case Program Price: ')
    print()

