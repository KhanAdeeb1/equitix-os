import pandas as pd
import numpy as np
from typing import Optional

def generate_ta_offer_data(num_records: int = 300) -> pd.DataFrame:
    """
    Demonstrates Python, Pandas, and Numpy skills by generating 
    statistically accurate simulated HR/TA data.
    
    Specifically models the Opendoor pain point: compensation-related 
    offer rejections for competitive technical roles.
    """
    print("Initializing TA Offer Data Engine...")
    np.random.seed(42)
    # Note: This Python engine uses numpy seed 42. 
    # The frontend dashboard uses an independent JS 
    # seeded random function with equivalent statistical 
    # properties (mean compa-ratio ~0.96, std ~0.10). 
    # Both datasets model the same workforce distribution 
    # — they are parallel simulations, not the same dataset.
    
    roles = ['Backend Engineer', 'Frontend Engineer', 'Data Scientist', 'Pricing Analyst', 'Field Operator']
    levels = ['L3', 'L4', 'L5']

    data = []
    for i in range(num_records):
        role = np.random.choice(roles)
        level = np.random.choice(levels)
        
        # Baseline market midpoint
        midpoint = np.random.randint(110000, 160000)
        
        # Simulate the offer compa-ratio (between 0.82 and 1.15)
        compa = np.round(np.random.uniform(0.82, 1.15), 2)
        offered_salary = int(midpoint * compa)
        
        # Engineered Inflection Point: Backend L4s reject offers < 95% market rate at a high volume
        if role == 'Backend Engineer' and level == 'L4' and compa < 0.95:
            outcome = np.random.choice(['Accepted', 'Declined'], p=[0.33, 0.67])
        elif compa < 0.90:
            outcome = np.random.choice(['Accepted', 'Declined'], p=[0.4, 0.6])
        elif compa >= 1.0:
            outcome = np.random.choice(['Accepted', 'Declined'], p=[0.85, 0.15])
        else:
            outcome = np.random.choice(['Accepted', 'Declined'], p=[0.6, 0.4])
            
        # Estimate the competing offer they took if they declined (5-12% higher)
        competing_offer = int(offered_salary * np.random.uniform(1.05, 1.12)) if outcome == 'Declined' else None
        
        data.append({
            'Candidate_ID': f'CAND-{i:03d}',
            'Role': role,
            'Level': level,
            'Market_Midpoint': midpoint,
            'Offered_Salary': offered_salary,
            'Compa_Ratio': compa,
            'Outcome': outcome,
            'Competing_Offer_Est': competing_offer
        })

    df = pd.DataFrame(data)
    
    # Feature Engineering: Create Risk Buckets for visualization
    bins = [0, 0.85, 0.90, 0.95, 1.0, 1.05, 2.0]
    labels = ['<0.85', '0.85-0.90', '0.90-0.95', '0.95-1.0', '1.0-1.05', '>1.05']
    df['CR_Bucket'] = pd.cut(df['Compa_Ratio'], bins=bins, labels=labels)
    
    df.to_csv('simulated_offers.csv', index=False)
    print("✅ TA Data Engine Complete: 'simulated_offers.csv' generated.")
    return df

def generate_employee_retention_data(num_records: int = 250) -> pd.DataFrame:
    """
    Generates N=250 workforce payload simulating core attributes like
    performance, tenure, and gender to model mid-year merit budgets 
    and pay equity compliance.
    """
    print("Initializing Employee Retention Data Engine...")
    np.random.seed(42)
    
    depts = ['Engineering', 'Product', 'Field Ops', 'Sales', 'Finance']
    levels = ['L3', 'L4', 'L5', 'L6']
    genders = ['Male', 'Female', 'Non-Binary']
    
    base_map = {'L3': 90000, 'L4': 130000, 'L5': 175000, 'L6': 220000}
    dept_mult = {'Engineering': 1.25, 'Product': 1.15, 'Field Ops': 0.85, 'Sales': 1.0, 'Finance': 0.95}

    data = []
    total_payroll = 0
    underpaid_cost = 0

    for i in range(num_records):
        dept = np.random.choice(depts)
        level = np.random.choice(levels)
        gender = np.random.choice(genders, p=[0.55, 0.40, 0.05])
        perf = np.random.randint(1, 6) # Rating 1-5
        tenure = np.round(np.random.uniform(0.5, 8.0), 1)
        
        midpoint = int(base_map[level] * dept_mult[dept])
        
        # Base normal distribution around 0.96 compa
        compa = np.random.normal(0.96, 0.10)
        
        # Introduce subtle structural variables for narrative testing
        if gender == 'Female':
            compa *= np.random.uniform(0.96, 1.0)
        if perf >= 4 and np.random.rand() > 0.5:
            compa *= 0.92 # Intentionally create underpaid high performers
            
        salary = int(midpoint * compa)
        compa_final = salary / midpoint
        
        risk = "Balanced"
        if compa_final < 0.90 and perf >= 4:
            risk = "Critical Flight Risk"
        elif compa_final > 1.15:
            risk = "Overpaid Outlier"

        total_payroll += salary
        if compa_final < 1.0:
            underpaid_cost += (midpoint - salary)

        data.append({
            'Employee_ID': f'E-{str(i+1).zfill(3)}',
            'Department': dept,
            'Level': level,
            'Gender': gender,
            'Current_Salary': salary,
            'Market_Midpoint': midpoint,
            'Compa_Ratio': round(compa_final, 3),
            'Performance_Rating': perf,
            'Tenure_Years': tenure,
            'Risk_Category': risk
        })

    df = pd.DataFrame(data)
    df.to_csv('employee_retention.csv', index=False)
    
    # Terminal Analytics Output
    print("\n--- 📊 WORKFORCE ANALYTICS SUMMARY ---")
    print(f"Total Headcount: {num_records}")
    print(f"Total Annual Payroll: ${total_payroll:,.0f}")
    print(f"Critical Flight Risks: {len(df[df['Risk_Category'] == 'Critical Flight Risk'])}")
    print(f"Cost to bring all underpaid to market 1.0: ${underpaid_cost:,.0f}")
    print("\nAvg Compa-Ratio by Department:")
    print(df.groupby('Department')['Compa_Ratio'].mean().round(3))
    
    print("\n✅ Retention Data Engine Complete: 'employee_retention.csv' generated.")
    return df

if __name__ == "__main__":
    _ = generate_ta_offer_data()
    _ = generate_employee_retention_data()
