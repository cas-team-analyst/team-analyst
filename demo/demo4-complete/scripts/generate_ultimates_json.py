import pandas as pd
import json

INPUT = "../ultimates/projected-ultimates.parquet"
OUTPUT = "../selections/ultimates.json"

df = pd.read_parquet(INPUT)

selections = []

# Weights dictionary: {age: (bf_weight, cl_weight)}
weights_map = {
    12: (1.00, 0.00),
    24: (0.75, 0.25),
    36: (0.50, 0.50),
    48: (0.25, 0.75)
}

for _, row in df.iterrows():
    period = int(row['period'])
    age = int(row['current_age'])
    measure = row['measure']
    
    cl_ult = row['cl_ultimate'] if pd.notna(row['cl_ultimate']) else 0
    bf_ult = row['bf_ultimate'] if pd.notna(row['bf_ultimate']) else 0
    
    # Apply weights
    if age in weights_map:
        bf_w, cl_w = weights_map[age]
        sel = (bf_ult * bf_w) + (cl_ult * cl_w)
        
        if bf_w == 1.0:
            methods = "100% BF"
        elif bf_w == 0.0:
            methods = "100% Chain Ladder"
        else:
            methods = f"{int(bf_w*100)}% BF / {int(cl_w*100)}% Chain Ladder"
            
        reasoning = f"{methods}\n\nMaturity-Based Weighting: Age {age} months. Transitioning from expected to actual experience."
    else:
        # Age > 48
        sel = cl_ult
        methods = "100% Chain Ladder"
        reasoning = f"{methods}\n\nMaturity-Based Weighting: Age {age} months. High maturity relies fully on Chain Ladder experience without expected loss drag."
        
    selections.append({
        "measure": measure,
        "period": period,
        "selection": float(sel),
        "reasoning": reasoning
    })

with open(OUTPUT, 'w') as f:
    json.dump(selections, f, indent=2)
    
print(f"Generated {len(selections)} ultimate selections")
