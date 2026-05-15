import pandas as pd


def compute_top_correlation(entries):
    """
    Вычисляет самую сильную корреляцию между метриками.
    """

    if len(entries) < 3:
        return None

    data = {
        "sleep": [],
        "energy": [],
        "mood": [],
        "productivity": [],
        "activity": []
    }

    for entry in entries:
        data["sleep"].append(float(entry.sleep))
        data["energy"].append(int(entry.energy))
        data["mood"].append(int(entry.mood))
        data["productivity"].append(int(entry.productivity))
        data["activity"].append(int(entry.activity))

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

    if abs_val <= 0.3:
        strength = "слабая"
    elif abs_val <= 0.7:
        strength = "умеренная"
    else:
        strength = "сильная"

    direction = "положительная" if best_value >= 0 else "отрицательная"

    return {
        "pair": list(best_pair),
        "value": round(float(best_value), 2),
        "strength": f"{strength} {direction}"
    }
