# Sort the unsorted list using counting method.
# The range of values must be known
unsorted_list = [5, 6, 7, 9, 8, 10]
max_value = max(unsorted_list)
count = [0 for i in range(max_value + 1)]
sorted_list = []
for i in unsorted_list:
    count[i] += 1

for i in range(0, max_value + 1):
    if count[i] > 0:
        for x in range(count[i]):
            sorted_list.append(i)

# sorted_lis = [i for i in range(0, max_value + 1) if count[i] > 0 for x in range(count[i])]
print(unsorted_list)
print(sorted_list)

# Method 2:
# 1. find the mean of the list
# 2. divide list into low and high, sorting with the mean
sorted_list_2 = []


def left_hand_sort(left_hand_list):
    if len(left_hand_list) <= 1:
        last_value = left_hand_list[0]
        sorted_list_2.append(last_value)
    else:
        mean = sum(left_hand_list) // len(left_hand_list)
        # sort the list
        sorted_left_hand_list = [i for i in left_hand_list if i <= mean]
        if len(sorted_left_hand_list) > 1:
            left_hand_sort(sorted_left_hand_list)
        elif len(sorted_left_hand_list) == 1:
            lowest_value = sorted_left_hand_list[0]
            sorted_list_2.append(lowest_value)
            unsorted_list.remove(lowest_value)
            left_hand_sort(unsorted_list)


left_hand_sort(unsorted_list)
print(f"result = {sorted_list_2}")
