import openai
import datetime
import os
import json

# Maximum number of API calls per day
MAX_API_CALLS = 200

def model(messages):
    # Load or initialize the count and date
    filename = 'prompts/api_calls.json'
    if os.path.isfile(filename):
        with open(filename, 'r') as f:
            data = json.load(f)
            call_count = data['count']
            last_call_date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
    else:
        call_count = 0
        last_call_date = datetime.date.today()

    # Check if it's a new day
    if datetime.date.today() != last_call_date:
        # If it's a new day, reset the count
        call_count = 0
        last_call_date = datetime.date.today()

    if call_count < MAX_API_CALLS:

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=messages
        )

        response_text = response['choices'][0]['message']['content']

        # Increment and save the count
        call_count += 1
        with open(filename, 'w') as f:
            json.dump({'count': call_count, 'date': str(last_call_date)}, f)
        return response_text

    else:
        print(f"API call limit of {MAX_API_CALLS} per day reached. Please wait until tomorrow.")


# EXAMPLE USAGE

# messages = [
#     {"role": "system", "content": "You are a helpful assistant."},
#     {"role": "user", "content": "Who won the world series in 2020?"},
#     {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
#     {"role": "user", "content": "Where was it played?"}
# ]
# response_text = model(messages)
# print(response_text)