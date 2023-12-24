import random

class RandomNumberGenerator:
    def __init__(self, choices):
        if not choices:
            raise ValueError("The 'choices' array must not be empty.")

        self.used_numbers = set()
        self.choices = choices

    def generate_random_number(self):
        remaining_choices = [num for num in self.choices if num not in self.used_numbers]

        if remaining_choices:
            selected_number = random.choice(remaining_choices)
            self.used_numbers.add(selected_number)
            return selected_number
        else:
            return None  # No valid choices left

