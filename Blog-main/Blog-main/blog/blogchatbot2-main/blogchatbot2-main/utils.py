import replicate
import time
import logging

# Initialize debounce variables
last_call_time = 0
debounce_interval = 2  # Set the debounce interval (in seconds) to your desired value

def debounce_replicate_run(llm, prompt, max_len, temperature, top_p, API_TOKEN,model_reference):
    global last_call_time
    print("last call time: ", last_call_time)

    # Get the current time
    current_time = time.time()

    # Calculate the time elapsed since the last call
    elapsed_time = current_time - last_call_time

    # Check if the elapsed time is less than the debounce interval
    if elapsed_time < debounce_interval:
        print("Debouncing")
        return "Hello! You are sending requests too fast. Please wait a few seconds before sending another request."

    # Update the last call time to the current time
    last_call_time = time.time()

    try:
        # Replace with the correct model reference
        model_reference = model_reference
        print("The API_TOKEN", API_TOKEN)

        # Initialize a client object with API token
        client = replicate.Client(api_token=API_TOKEN)

        # Attempt to call the Replicate API
        output = client.run(
            model_reference,
            input={"prompt": prompt + "Assistant: ", "max_length": max_len, "temperature": temperature, "top_p": top_p, "repetition_penalty": 1}
        )
        return output
    except replicate.exceptions.ReplicateError as e:
        # Handle specific Replicate errors
        logging.error(f"ReplicateError: {e}")
        logging.error(f"Title: {e.title}")
        logging.error(f"Status Code: {e.status}")
        logging.error(f"Detail: {e.detail}")
        return f"ReplicateError: {e.title} - {e.detail}"
    except Exception as e:
        # Handle other exceptions
        logging.exception("Error calling Replicate API:")
        return "An error occurred while communicating with the LLaMA2 model. Please try again later."

