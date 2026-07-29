import os
import pandas as pd
import anthropic
from typing import Optional

def generate_executive_memo(df: pd.DataFrame) -> Optional[str]:
    """
    Demonstrates LLM integration and Prompt Engineering skills using 
    the Anthropic Python SDK.
    
    Takes the simulated dataset, identifies the specific attrition risk,
    and drafts an executive strategy memo.
    """
    # Isolate the specific Backend L4 problem for the AI prompt
    be_l4 = df[(df['Role'] == 'Backend Engineer') & (df['Level'] == 'L4')]
    declines = be_l4[(be_l4['Compa_Ratio'] < 0.95) & (be_l4['Outcome'] == 'Declined')]
    
    if len(declines) == 0:
        print("Not enough data to generate a meaningful memo.")
        return None
        
    avg_gap = (declines['Competing_Offer_Est'] - declines['Offered_Salary']).mean()
    decline_rate = (len(declines) / len(be_l4[be_l4['Compa_Ratio'] < 0.95])) * 100
    
    prompt = f"""
    You are the Lead People Analytics Specialist at Opendoor. 
    Write a concise, one-page offer strategy memo to the Global TA Director.
    
    Data Context from our ATS integration:
    - Role: Backend Engineer (L4)
    - Critical Issue: Offers extended below a 95% compa-ratio are currently being rejected at a {decline_rate:.1f}% rate.
    - Talent Loss: We have lost {len(declines)} vetted candidates in this bracket this quarter.
    - Financial Gap: Competing offers are beating our initial packages by an average of ${avg_gap:,.0f}.
    
    Memo Requirements:
    1. Executive Summary: State the problem bluntly (we are losing top technical talent due to initial offers sitting below the market inflection point).
    2. The Data Proof: Cite the rejection rate and the exact dollar gap.
    3. The Recommendation: Propose a strict new policy that all Backend L4 offers must be modeled at a minimum 98% compa-ratio.
    
    Tone: Direct, operator-focused, data-driven.
    """
    
    print("Connecting to Anthropic API...")
    try:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not found.")
            
        client = anthropic.Anthropic(api_key=api_key)
        
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        
        memo = response.content[0].text
        print("\n--- 📝 EXECUTIVE MEMO GENERATED ---\n")
        print(memo)
        return memo
        
    except Exception as e:
        print(f"❌ API Execution Error: {e}")
        return None

def generate_equity_brief(df: pd.DataFrame) -> Optional[str]:
    """
    Analyzes the employee retention dataframe for pay equity gaps
    and queries Claude to generate a formal compliance brief for HR/Legal.
    """
    if df.empty or 'Gender' not in df.columns:
        print("Data missing or improperly formatted for equity audit.")
        return None

    try:
        # Calculate Unadjusted (Raw) Pay Gap
        male_avg = df[df['Gender'] == 'Male']['Compa_Ratio'].mean()
        female_avg = df[df['Gender'] == 'Female']['Compa_Ratio'].mean()
        unadjusted_gap = (female_avg / male_avg) * 100 if male_avg else 100

        # Calculate Adjusted Pay Gap (Controlling for Dept and Level)
        # We find the mean of the ratio of female to male compa within each cohort
        cohorts = df.groupby(['Department', 'Level', 'Gender'])['Compa_Ratio'].mean().unstack()
        # Drop rows missing either Male or Female data
        valid_cohorts = cohorts.dropna(subset=['Male', 'Female'])
        
        if len(valid_cohorts) > 0:
            adjusted_gap = (valid_cohorts['Female'] / valid_cohorts['Male']).mean() * 100
        else:
            adjusted_gap = unadjusted_gap

        prompt = f"""
        You are the Director of Total Rewards presenting a Pay Equity Compliance Brief to the Chief People Officer (CPO) and General Counsel.
        
        Audit Data (N={len(df)} employees):
        - Unadjusted Pay Gap (Raw Average Female-to-Male): {unadjusted_gap:.1f} cents on the dollar.
        - Adjusted Pay Gap (Controlling for Department & Job Level): {adjusted_gap:.1f} cents on the dollar.
        
        Write a formal, 3-paragraph compliance brief covering:
        1. Overview: State the results of the recent demographic audit and quote the raw unadjusted gap.
        2. Adjusted Analysis: Explain that when controlling for identical departments and levels, systemic equity improves significantly to {adjusted_gap:.1f} cents, proving our baseline bands are structurally sound.
        3. Next Steps: Advise HR Business Partners to review the remaining fractional variance (driven mostly by tenure) during the upcoming promotion cycle to eliminate unintentional bias.
        
        Tone: Professional, legally cautious, analytical.
        """

        print("Connecting to Anthropic API for Equity Brief...")
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not found.")

        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}]
        )
        
        memo = response.content[0].text
        print("\n--- ⚖️ EQUITY COMPLIANCE BRIEF GENERATED ---\n")
        print(memo)
        return memo

    except anthropic.APIError as e:
        err_msg = f"❌ Anthropic API Communication Error: {e}"
        print(err_msg)
        return err_msg
    except Exception as e:
        err_msg = f"❌ General Execution Error during Equity Brief generation: {e}"
        print(err_msg)
        return err_msg

if __name__ == "__main__":
    try:
        # Note: You must run data_engine.py first to generate these files.
        ta_data = pd.read_csv('simulated_offers.csv')
        generate_executive_memo(ta_data)
        
        retention_data = pd.read_csv('employee_retention.csv')
        generate_equity_brief(retention_data)
        
    except FileNotFoundError as fnf:
        print(f"File not found. Please run data_engine.py first. Details: {fnf}")