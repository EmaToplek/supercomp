"""
Print an overview of the synthetic training data.

Run from the backend folder: python -m scripts.generate_synthetic
"""

from app.generators.synthetic import generate_activities


def main():
    for activity in generate_activities():
        duration_min = len(activity.samples) // 60
        distance_km = activity.samples["distance"].iloc[-1] / 1000
        print(activity.start.date(), activity.kind, duration_min, "min", round(distance_km, 1), "km")


if __name__ == "__main__":
    main()