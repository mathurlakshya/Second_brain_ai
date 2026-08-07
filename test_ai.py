from ai.gemini import ask_jarvis

while True:

    question = input("You : ")

    if question.lower() == "exit":
        break

    answer = ask_jarvis(question)

    print("\nJARVIS:\n")

    print(answer)

    print()