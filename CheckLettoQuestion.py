import json
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
#from openai import OpenAI
import openai

# Function to process the input JSON, send requests to ChatGPT, and display results
def process_input():
    try:
        input_data = input_text.get("1.0", tk.END).strip()
        input_json = json.loads(input_data)
  
        # Set your OpenAI API key from JSON input file
        # openai.api_key = input_json["aiKey"]
        
        # Extract subquestions with correct answers
        sub_questions = []
        for question in input_json["questions"]:
            for sub_question in question.get("subQuestions", []):
                if "korrekteLoesung" in sub_question and sub_question["korrekteLoesung"]:
                    sub_questions.append({
                        "idTestfrage": question["idTestfrage"],
                        "angabe": sub_question["angabe"],
                        "korrekteLoesung": sub_question["korrekteLoesung"],
                        "inputs": [{
                            "idTestDetail": input_item["idTestDetail"],
                            "text": input_item["text"],
                            "name": input_item["name"],
                            "idUser": input_item["idUser"]
                        } for input_item in sub_question["inputs"]]
                    })
        
        # Build request JSON for ChatGPT
        gpt_requests = [{
            "idTestfrage": sub_question["idTestfrage"],
            "angabe": sub_question["angabe"],
            "korrekteLoesung": sub_question["korrekteLoesung"],
            "inputs": sub_question["inputs"]
        } for sub_question in sub_questions]

        # Create a prompt explaining how to provide feedback for the student's answers based on the JSON data
        prompt = (
            "Du erhältst ein JSON-Dokument, das Informationen zu mehreren Prüfungsfragen enthält. Jede Prüfungsfrage kann mehrere Unterfragen (subQuestions) haben. "
            "Zu jeder Unterfrage gibt es eine Musterlösung und die Antworten der Schüler. "
            "Deine Aufgabe ist es, die Schülerantworten zu bewerten und Feedback zu geben, wie die Antworten verbessert werden können. "
            "Verwende die Musterlösung als Referenz und gib ein detailliertes, aber leicht verständliches Feedback für jede Schülerantwort. "
            "Als Antwort wird nur ein JSON-Dokument erwartet, das in folgendem Format strukturiert ist: "
            "[ { \"idTestfrage\": <idTestfrage>, \"subQuestions\": [ { \"bewertungen\": [ { \"idTestDetail\": <idTestDetail>, \"feedback\": \"<Feedback>\", \"bewertung\": <Bewertung in Prozent> } ] } ] } ] "
            "Gib die Antwort bitte nur als reinen JSON-String ohne zusätzliche Erklärungen oder Formatierungen zurück. "
            "Hier ist das JSON-Dokument: " + json.dumps(gpt_requests)
        )
      
        # Send the request to ChatGPT
        client = openai.OpenAI(
            # This is the default and can be omitted
            api_key=input_json["aiKey"],
        )            
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="gpt-4o-mini",
#            model="gpt-3.5-turbo",
            max_tokens=2000
        )      
        # Extract and modify responses
        feedbacks = response.choices[0].message.content
        if feedbacks.startswith("```json"):
            feedbacks = feedbacks.splitlines()[1:-1]
            feedbacks = "\n".join(feedbacks)
              
        print(feedbacks)     
        feedbacks = json.loads(feedbacks)   
        for feedback in feedbacks:
            for question in input_json["questions"]:
                if question["idTestfrage"] == feedback["idTestfrage"]:
                    feedback["name"] = question.get("name", "Unbekannt")
                    for sub_question, feedback_sub_question in zip(question.get("subQuestions", []), feedback.get("subQuestions", [])):
                        for input_item, bewertung in zip(sub_question["inputs"], feedback_sub_question["bewertungen"]):
                            if input_item["idTestDetail"] == bewertung["idTestDetail"]:
                                bewertung["name"] = input_item["name"]
                                bewertung["idUser"] = input_item["idUser"]
                                bewertung["bewertung"] = bewertung.get("bewertung", "0")
        
        # Clear previous feedbacks in the output frame
        for widget in output_frame.winfo_children():
            widget.destroy()
        
        # Display feedback in the GUI
        sub_question_notebook = ttk.Notebook(output_frame)
        sub_question_notebook.pack(fill=tk.BOTH, expand=True)

        question_index = 0
        for question in feedbacks:
            question_index += 1
            sub_question_index = 0
            for sub_question in question["subQuestions"]:
                sub_question_index += 1
                
                sub_question_frame = tk.Frame(sub_question_notebook)
                sub_question_notebook.add(sub_question_frame, text=f"{question_index}.{sub_question_index}")
                
                student_notebook = ttk.Notebook(sub_question_frame)
                student_notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                for bewertung in sub_question["bewertungen"]:
                    student_frame = tk.Frame(student_notebook)
                    student_notebook.add(student_frame, text=bewertung["name"])
                    
                    name_label = tk.Label(student_frame, text=f"Schülername: {bewertung['name']}", anchor='w')
                    name_label.pack(fill=tk.X, padx=5, pady=(10, 2))
                    
                    feedback_label = tk.Label(student_frame, text="Feedback:", anchor='w')
                    feedback_label.pack(fill=tk.X, padx=5)
                    feedback_text = scrolledtext.ScrolledText(student_frame, wrap=tk.WORD, width=80, height=5)
                    feedback_text.insert(tk.END, bewertung["feedback"])
                    feedback_text.pack(fill=tk.X, padx=5, pady=2)
                    
                    bewertung_label = tk.Label(student_frame, text="Bewertung:", anchor='w')
                    bewertung_label.pack(fill=tk.X, padx=5)
                    bewertung_entry = tk.Entry(student_frame, width=10)
                    bewertung_entry.insert(0, f"{bewertung['bewertung']}%")
                    bewertung_entry.pack(fill=tk.X, padx=5, pady=(2, 10))

    except json.JSONDecodeError:
        messagebox.showerror("Fehler", "Eingabedaten sind kein gültiger JSON-String.")
    except Exception as e:
        messagebox.showerror("Fehler", str(e))

# Set up GUI
root = tk.Tk()
root.title("ChatGPT Test Feedback")
root.geometry("800x800")

# Input label and text area
input_label = tk.Label(root, text="Eingabe JSON String:")
input_label.pack()
input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=10)
input_text.pack()

# Process button
process_button = tk.Button(root, text="Test bewerten", command=process_input)
process_button.pack()

# Output label
output_label = tk.Label(root, text="Feedback und Bewertung:")
output_label.pack()

# Output frame with scrollbar
output_container = tk.Frame(root)
output_container.pack(fill=tk.BOTH, expand=True)
output_canvas = tk.Canvas(output_container)
output_scrollbar = tk.Scrollbar(output_container, orient=tk.VERTICAL, command=output_canvas.yview)
output_frame = tk.Frame(output_canvas)
output_frame.bind(
    "<Configure>",
    lambda e: output_canvas.configure(scrollregion=output_canvas.bbox("all"))
)
output_canvas.create_window((0, 0), window=output_frame, anchor="nw")
output_canvas.configure(yscrollcommand=output_scrollbar.set)

output_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
output_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Run the GUI loop
root.mainloop()
