import json, random
from collections import defaultdict

def calculate_probabilities(word_data):
    """
    Updates the word data to include probabilities for next and previous words.
    """
    for word_entry in word_data.values():
        total_next = sum(word_entry['next'].values())
        total_prev = sum(word_entry['prev'].values())

        # Calculate next probabilities safely
        word_entry['next_prob'] = {
            next_word: (count / total_next) if total_next > 0 else 0
            for next_word, count in word_entry['next'].items()
        }

        # Calculate previous probabilities safely
        word_entry['prev_prob'] = {
            prev_word: (count / total_prev) if total_prev > 0 else 0
            for prev_word, count in word_entry['prev'].items()
        }

def update_word_data(information_array, training_input_array):
    """
    Updates the word data structure with new training input.
    """
    for i, word in enumerate(training_input_array):
        if word not in information_array:
            information_array[word] = {
                "prev": defaultdict(int),
                "next": defaultdict(int),
                "next_prob": {},
                "prev_prob": {},
            }

        # Update previous word relationship
        if i > 0:
            prev_word = training_input_array[i - 1]
            if prev_word not in information_array:
                information_array[prev_word] = {
                    "prev": defaultdict(int),
                    "next": defaultdict(int),
                    "next_prob": {},
                    "prev_prob": {},
                }
            information_array[word]['prev'][prev_word] += 1

        # Update next word relationship
        if i < len(training_input_array) - 1:
            next_word = training_input_array[i + 1]
            if next_word not in information_array:
                information_array[next_word] = {
                    "prev": defaultdict(int),
                    "next": defaultdict(int),
                    "next_prob": {},
                    "prev_prob": {},
                }
            information_array[word]['next'][next_word] += 1

def run_model(prompt, information_array, max_length=5):
    """
    Generate a completion for the given prompt based on the word data.
    """
    words = prompt.split()
    
    if not words:
        return "Invalid prompt. Please provide one or more words."

    current_word = words[-1]
    completion = words[:]

    for _ in range(max_length - len(words)):
        if current_word in information_array:
            next_word_probs = information_array[current_word].get('next_prob')
            if next_word_probs:
                # Choose a next word based on weighted random choice
                next_word = random.choices(
                    list(next_word_probs.keys()),
                    weights=next_word_probs.values(),
                    k=1
                )[0]
                completion.append(next_word)
                current_word = next_word
            else:
                break  # No known next word, so stop generating
        else:
            return "Word not found in training data."

    return " ".join(completion)

if __name__ == "__main__":
    information_array = {}

    try:
        # Load existing data if available
        with open("word_data.json", "r") as file:
            information_array = json.load(file)
    except FileNotFoundError:
        print("No existing training data found. Starting fresh.")

    while True:
        print("\nJotalea's AI (from scratch)")
        print("1. Train the model with a new sentence")
        print("2. Train the model with a text file")
        print("3. Run the model with a prompt")
        print("4. Quit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            prompt = input("Enter a sentence: ").lower()
            training_input_array = prompt.split(" ")
            update_word_data(information_array, training_input_array)
            calculate_probabilities(information_array)
            print("Training complete. Model updated.")

        elif choice == "2":
            file_name = input("Enter the path of the text file: ").strip()
            try:
                with open(file_name, "r") as file:
                    text = file.read().lower()
                    training_input_array = text.split()
                    update_word_data(information_array, training_input_array)
                    calculate_probabilities(information_array)
                    print(f"Model updated with content from {file_name}.")
            except FileNotFoundError:
                print(f"The file {file_name} was not found.")

        elif choice == "3":
            prompt = input("Enter a one or two-word prompt: ").lower()
            result = run_model(prompt, information_array)
            print(f"Output: {result}")

        elif choice == "4":
            # Save the model and exit
            with open("word_data.json", "w") as file:
                json.dump(information_array, file, indent=4)
            print("Model saved. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")
