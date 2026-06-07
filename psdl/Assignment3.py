import random
from datetime import datetime, timedelta

n = int(input("Enter number of people in a group : "))

def birthDate(day_num):
    start_date = datetime(2026,1,1)

    final_date = start_date + timedelta(days = day_num)

    return final_date.strftime("%d-%m-%Y")

def trail():
    population = list(range(365))

    sample = random.choices(population, k = n)

    seen = set()
    dupes = set()

    for x in sample :
        if x in seen:
            dupes.add(x)
        else:
            seen.add(x)
    return sample, list(dupes), len(sample) != len(set(sample))

dup_count = 0
output_sample = []
output_dup = []

trails = int(input("Enter the number of trails : "))

for _ in range(trails):
    sample, dupes, has_dup = trail()

    if has_dup:
        dup_count += 1

        if not output_dup :
            output_sample = sample
            output_dup = dupes

probability = dup_count / trails

print("\nSample Birthdays :")

for day in output_sample:
    print(birthDate(day))

print("\nDuplicate Birthdays Found :")

if output_dup:

    for day in output_dup:
        print(birthDate(day))

else:
    print("No duplicates")
print("\nProbability of at least one duplicate : ", probability)
