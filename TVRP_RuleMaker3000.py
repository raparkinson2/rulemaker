import tkinter as tk
from tkinter import filedialog, ttk
import pandas as pd

def select_source_file():
    """Function to select source file."""
    path = filedialog.askopenfilename(title="Select Source CSV", filetypes=[("CSV files", "*.csv")])
    source_file_path.set(path)

def select_output_file():
    """Function to select output file location."""
    path = filedialog.asksaveasfilename(title="Select Output CSV Location", defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    output_file_path.set(path)

def ensure_continuous_sequence(df):
    """Ensure that for each DEPTID_CF, there is a continuous sequence of SB_APRV_LEVEL, and add any missing levels."""
    all_deptids = df['DEPTID_CF'].unique()
    max_approval_level = df['SB_APRV_LEVEL'].max()
    all_levels = list(range(1, max_approval_level + 1))
    all_combinations = pd.MultiIndex.from_product([all_deptids, all_levels], names=['DEPTID_CF', 'SB_APRV_LEVEL'])

    # Drop duplicate rows based on DEPTID_CF and SB_APRV_LEVEL
    df = df.drop_duplicates(subset=['DEPTID_CF', 'SB_APRV_LEVEL']).set_index(['DEPTID_CF', 'SB_APRV_LEVEL'])

    df_aligned = df.reindex(all_combinations).reset_index()
    df_aligned = df_aligned.groupby('DEPTID_CF').apply(lambda group: group.ffill()).reset_index(drop=True)
    return df_aligned

def calculate_limits(business_unit, sb_aprv_level):
    """Determine the lower and upper limits based on the business unit and approval level."""
    limits = {
        "CHICO": {
            1: (100000.01, 999999999.99),
            2: (20000.01, 100000.00),
            3: (500.01, 20000.00),
            4: (0.01, 500.00)
        },
        "FRSNO": {
            1: (100000.01, 999999999.99),
            2: (50000.01, 100000.00),
            3: (5000.01, 50000.00),
            4: (0.01, 5000.00)
        },
        "FRATH": {
            1: (100000.01, 999999999.99),
            2: (50000.01, 100000.00),
            3: (5000.01, 50000.00),
            4: (0.01, 5000.00)
        }
    }
    return limits[business_unit].get(sb_aprv_level, (0, 0))

def reverse_modify_business_unit(modified_business_unit):
    """Transform modified business unit values back to their original form."""
    reverse_replacements = {
        "CHXCO": "CHICO",
        "FRXNO": "FRSNO",
        "FRXTH": "FRATH"
    }
    return reverse_replacements.get(modified_business_unit, modified_business_unit)

def modify_business_unit(business_unit):
    """Transform business unit values."""
    replacements = {
        "CHICO": "oneOf|CHXCO",
        "FRSNO": "oneOf|FRXNO",
        "FRATH": "oneOf|FRXTH"
    }
    return replacements.get(business_unit, business_unit)

def replace_text(string):
    if string == "CHICO" or string == "FRSNO" or string == "FRATH":
        # Replace the BU code with the intended conditional value(s)
        if string == "CHICO":
            string = "CHICO"
        elif string == "FRSNO":
            string = "FRSNO"
        elif string == "FRATH":
            string = "FRSNO"
        # Add more conditions if needed
        
    return string

def transform_data():
    """Function to process the source file and save the output."""
    df = pd.read_csv(source_file_path.get(), dtype={'SB_LIMIT_AMT': str})
    df = ensure_continuous_sequence(df)
    transformed_data = []

    for (sb_aprv_level, csu_calstedupersid, business_unit), group in df.groupby(['SB_APRV_LEVEL', 'CSU_CALSTEDUPERSID', 'BUSINESS_UNIT']):
        rule_group_name = f"DOA Approval: Level {sb_aprv_level}"
        rule_name = f"DOA RULE: {csu_calstedupersid}"
        deptids = group['DEPTID_CF'].unique()
        lower_limit, upper_limit = calculate_limits(business_unit, sb_aprv_level)
        document_total = f"Between|{lower_limit}|{upper_limit}|USD"
        modified_bu = modify_business_unit(business_unit)
        
        for i, chunk_deptids in enumerate([deptids[x:x+49] for x in range(0, len(deptids), 49)]):
            rule_suffix = f":{i+1}" if i > 0 else ""
            rule_internal_name = f"{rule_name}{rule_suffix}"
            rule_display_name = f"{rule_name}{rule_suffix}"
            # Get the actual business unit using reverse mapping
            actual_bu = reverse_modify_business_unit(modified_bu)
            deptids_str = f"DeptID|oneOf|{'|'.join([str(val) + '_' + replace_text(business_unit) for val in deptids])}"
            transformed_data.extend([
                [rule_group_name, rule_group_name, "", rule_internal_name, rule_display_name, "", csu_calstedupersid, "", "FALSE", "TRUE", "DocumentTotal", document_total],
                [rule_group_name, rule_group_name, "", rule_internal_name, rule_display_name, "", csu_calstedupersid, "", "FALSE", "TRUE", "BusinessUnit", modified_bu],
                [rule_group_name, rule_group_name, "", rule_internal_name, rule_display_name, "", csu_calstedupersid, "", "FALSE", "TRUE", "CustomFieldValueMulti", deptids_str]
            ])

    columns = ["Rule Group Internal Name", "Rule Group Display Name", "Rule Group Description", "Rule Internal Name", "Rule Display Name", "Rule Description", "RUle Approvers", "Implicit Approvers", "Auto Approve", "Active", "Type", "Value"]
    transformed_df = pd.DataFrame(transformed_data, columns=columns)
    transformed_df.to_csv(output_file_path.get(), index=False)

app = tk.Tk()
app.title("DOA App")

frame = ttk.Frame(app, padding=10)
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

source_file_path = tk.StringVar()
output_file_path = tk.StringVar()

ttk.Label(frame, text="Select Source CSV File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
ttk.Button(frame, text="Browse", command=select_source_file).grid(row=0, column=1, padx=5, pady=5)
ttk.Label(frame, textvariable=source_file_path).grid(row=0, column=2, padx=5, pady=5)

ttk.Label(frame, text="Select Output CSV Location:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
ttk.Button(frame, text="Browse", command=select_output_file).grid(row=1, column=1, padx=5, pady=5)
ttk.Label(frame, textvariable=output_file_path).grid(row=1, column=2, padx=5, pady=5)

ttk.Button(frame, text="Transform Data", command=transform_data).grid(row=2, columnspan=3, pady=10)

app.mainloop()
