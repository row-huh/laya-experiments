from typesafe_sdk import Choice, Noul, Score, TypeSafeClient
import os
import time

# Set the environment variables
os.environ["TYPESAFE_BASE_URL"] = "http://localhost:11434"
os.environ["TYPESAFE_API_KEY"] = "ollama"
os.environ["TYPESAFE_DEFAULT_MODEL"] = "nimble"

ticket = "I was charged twice. Please refund the extra payment."
questions = {
    "team": Choice(
        instructions="Which team should handle this ticket?",
        criteria={
            "billing": "Payments and refunds",
            "technical": "Bugs and integrations",
            "other": "None of the above",
        },
    ),
    "refund": Noul(
        instructions="Does the customer explicitly ask for a refund?",
    ),
    "urgency": Score(
        instructions="How urgent is this ticket?",
        criteria=["Routine", "Soon", "Urgent"],
    ),
}


start_time = time.time()

with TypeSafeClient(timeout=120) as client:
    result = client.system_one(
        state={"ticket": ticket},
        questions=questions,
    ) 


end_time = time.time()

total_time = end_time - start_time
print(result.choices["team"].choice)   # billing
print(result.nouls["refund"].noul)     # 0.997
print(result.scores["urgency"].score)  # 0.69 

print("\n\nExecution time: {:.2f} seconds".format(total_time))