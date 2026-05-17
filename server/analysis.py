import pandas as pd


def compute_top_correlation(entries):

    if len(entries) < 3:
        return None

    data = {
        "сон": [],
        "энергия": [],
        "натсроение": [],
        "продуктивность": [],
        "активность": []
    }

    for entry in entries:
        data["сон"].append(float(entry.sleep))
        data["энергия"].append(int(entry.energy))
        data["натсроение"].append(int(entry.mood))
        data["продуктивность"].append(int(entry.productivity))
        data["активность"].append(int(entry.activity))

    df = pd.DataFrame(data)

    corr_matrix = df.corr(method="pearson")

    best_pair = None
    best_value = 0

    columns = corr_matrix.columns

    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            value = corr_matrix.iloc[i, j]

            if abs(value) > abs(best_value):
                best_value = value
                best_pair = (columns[i], columns[j])

    abs_val = abs(best_value)

    if abs_val <= 0.5:
        strength = "слабая"
    elif abs_val <= 0.75:
        strength = "умеренная"
    else:
        strength = "сильная"

    direction = "положительная корреляция" if best_value >= 0 else "отрицательная корреляция"

    return {
        "pair": list(best_pair),
        "value": round(float(best_value), 2),
        "strength": f"{strength} {direction}"
    }
