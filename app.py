from flask import Flask, request, render_template
import openai
from dotenv import load_dotenv
import os
import time
import logging
from datetime import datetime

load_dotenv()

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()
model = "gpt-4-turbo-preview"

assistant_id = "asst_qXK4TGu8TH7Al37hPC0WYZtP"
thread_id = "thread_OY6sk5WHi45eV1B9FiRvGo5B"

conversation_history = []

def wait_for_run_completion(client, thread_id, run_id, sleep_interval=5):
    while True:
        try:
            run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
            if run.completed_at:
                # Get messages here once Run is completed!
                messages = client.beta.threads.messages.list(thread_id=thread_id)
                last_message = messages.data[0]
                response = last_message.content[0].text.value
                return response
        except Exception as e:
            logging.error(f"An error occurred while retrieving the run: {e}")
            return "An error occurred. Please try again."
        time.sleep(sleep_interval)

@app.route('/chat', methods=['POST'])
def chat():
    user_msg = request.form['message']
    
    # Create a Message in the thread
    message = client.beta.threads.messages.create(
        thread_id=thread_id, role="user", content=user_msg
    )

    # Run our Assistant
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions="be helpful and provide accurate answers",
    )
    # Wait for run completion and get the response
    response = wait_for_run_completion(client, thread_id, run.id)
    conversation_history.insert(0, (user_msg, response))

    print(user_msg)
    print(response)
    # Pass the response to your template
    return render_template('index.html', response=conversation_history)

@app.route('/')
def index():
    # Render the form without any response
    return render_template('index.html', response=[])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
