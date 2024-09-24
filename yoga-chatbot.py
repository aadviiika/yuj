import pandas as pd
from rapidfuzz import process

# Load the knowledge base from CSV file
knowledge_base = None
try:
    # Use 'on_bad_lines' to skip problematic lines
    knowledge_base = pd.read_csv('yuj.csv', quoting=1, on_bad_lines='skip')
except Exception as e:
    print(f"Error loading CSV: {e}")

def normalize_input(user_input):
    return user_input.strip().lower()

def get_closest_symptom(user_symptom, symptoms_list):
    # Find the closest symptom in the dataset using fuzzy matching
    closest_match = process.extractOne(user_symptom, symptoms_list)
    return closest_match[0] if closest_match else None

def suggest_treatments(symptoms, age, gender):
    if knowledge_base is None:
        return None, None, "Knowledge base not available. Unable to provide suggestions."

    symptoms_normalized = [normalize_input(symptom) for symptom in symptoms]
    symptoms_list = knowledge_base['Symptom'].tolist()  # Keep original case for checking

    recommendations = {}
    
    for symptom_normalized in symptoms_normalized:
        # Directly check for exact match of abbreviation or full name
        closest_symptom = None
        for s in symptoms_list:
            if symptom_normalized == s.lower() or symptom_normalized in s.lower():
                closest_symptom = s
                break
        
        if closest_symptom is None:
            # If no match found, find the closest matching symptom using fuzzy matching
            closest_symptom = get_closest_symptom(symptom_normalized, symptoms_list)

        if closest_symptom is None:
            recommendations[symptom_normalized] = "I'm sorry, I couldn't find any suggestions for that symptom."
        else:
            # Filter the knowledge base for the given closest symptom
            suggestions = knowledge_base[knowledge_base['Symptom'] == closest_symptom]
            asanas = suggestions['Yoga Asanas'].values[0].split('; ')
            pressure_points = suggestions['Pressure Points'].values[0].split('; ')
            notes = suggestions['Notes'].values[0]

            # Check for serious conditions
            serious_conditions = ['could be serious', 'mental']
            if isinstance(notes, str) and any(condition in notes.lower() for condition in serious_conditions):
                notes_message = "Note: If you're experiencing severe symptoms, please seek professional help."
            else:
                notes_message = None

            recommendations[closest_symptom] = {
                'asanas': asanas,
                'pressure_points': pressure_points,
                'notes_message': notes_message
            }

    return recommendations

# Start chatbot interaction
def chat_with_bot():
    if knowledge_base is None:
        print("Knowledge base is not loaded. Please check the CSV file.")
        return

    while True:
        symptom_input = input("Describe your symptoms (e.g., back pain, headache, anxiety). Type 'quit', 'bye', or 'end' to exit.\nYou: ")
        if symptom_input.lower() in ['quit', 'bye', 'end']:
            break
        age = input("Please enter your age: ")
        gender = input("Please specify your gender (girl, female, boy, male, other, etc.): ")

        # Split input by common delimiters (like 'and' and ',') and remove extra spaces
        symptoms = [s.strip() for s in symptom_input.replace(',', ' and ').split(' and ')]

        recommendations = suggest_treatments(symptoms, age, gender)

        for symptom, recommendation in recommendations.items():
            if isinstance(recommendation, str):
                print(f"For '{symptom}': {recommendation}")
            else:
                asanas = recommendation['asanas']
                pressure_points = recommendation['pressure_points']
                notes_message = recommendation['notes_message']
                
                print(f"### Recommended Yoga Asanas for '{symptom}':\n\n- " + "\n- ".join(asanas))
                print(f"\n### Recommended Acupressure Points for '{symptom}':\n\n- " + "\n- ".join(pressure_points))
                if notes_message:
                    print(f"\n{notes_message}")

        # Additional note at the end of each response
        print("\nIf symptoms persist or get unbearable, please seek professional help.")
        print('\n\n\n')

# Start the chatbot
chat_with_bot()
