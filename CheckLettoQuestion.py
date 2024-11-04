import json
import configparser
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import openai

# Load settings from the ini file
config = configparser.ConfigParser()
config.read('settings.ini')
max_tokens_setting = int(config['DEFAULT'].get('max_tokens', 2000))

# Function to process the input JSON, send requests to ChatGPT, and display results
def process_input():
    # try:
        input_data = input_text.get("1.0", tk.END).strip()
        input_json = json.loads(input_data)
  
        # Set your OpenAI API key from JSON input file
        openai.api_key = input_json["aiKey"]
        
        # Extract subquestions with correct answers
        sub_questions = []
        for question in input_json["questions"]:
            for sub_question in question.get("subQuestions", []):
                if "korrekteLoesung" in sub_question and sub_question["korrekteLoesung"]:
                    sub_questions.append({
                        "subquestionId": sub_question["idSq"],
                        "subquestion": sub_question["angabe"],
                        "answerReference": sub_question["korrekteLoesung"],
                        "gradingPolicy": sub_question["beurteilungsAnweisung"],                        
                        "answers": [{
                            "studentQuestionId": input_item["idTestDetail"],
                            "studentAnswer": input_item["text"],
                            "studentName": input_item["name"],
                            "studentId": input_item["idUser"]
                        } for input_item in sub_question["inputs"]]
                    })
        
        # Build request JSON for ChatGPT
        gpt_requests = [{
            "subquestionId": sub_question["subquestionId"],
            "subquestion": sub_question["subquestion"],
            "answerReference": sub_question["answerReference"],
            "gradingPolicy": sub_question["gradingPolicy"],                        
            "answers": [{
                "studentQuestionId": answer_item["studentQuestionId"],
                "studentAnswer": answer_item["studentAnswer"],
            } for answer_item in sub_question["answers"]]
        } for sub_question in sub_questions]
 
        #check the input.json
        # print(json.dumps(gpt_requests))

        # Load prompt from file and add JSON data
        with open('Prompt.txt', 'r', encoding='utf-8') as file:
            template = file.read()

        prompt = template.replace("{INPUT_JSON}", json.dumps(gpt_requests))

        #check the final promt
        #print(prompt)
        #return
        
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
            max_tokens=max_tokens_setting
        )     
        
        # Extract token usage information
        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        tokens_used = response.usage.total_tokens
        print(f"Tokens: Promt {prompt_tokens}, completion {completion_tokens}, Total used: {tokens_used}")        
        
        # Extract and modify responses
        feedbacks = response.choices[0].message.content
        if feedbacks.startswith("```json"):
            feedbacks = feedbacks.splitlines()[1:-1]
            feedbacks = "\n".join(feedbacks)
              
        # Save feedbacks to response.json
        with open('response.json', 'w', encoding='utf-8') as response_file:
            response_file.write(feedbacks)

        #with open('response.json', 'r', encoding='utf-8') as file:
        #    feedbacks = file.read()      
        
        #add user data to responce (result visualisation)
        subQuestionResponces = json.loads(feedbacks)   
        for subQuestionResponce in subQuestionResponces:
            for sub_question in sub_questions:
                if sub_question["subquestionId"] == subQuestionResponce["subquestionId"]:                    
                    subQuestionResponce["name"] = sub_question.get("name", "Unbekannt")
                    for awsner, feedback in zip (sub_question.get("answers", []), subQuestionResponce.get("feedbacks", [])):
                        if awsner["studentQuestionId"] == feedback["studentQuestionId"]:
                            feedback["studentName"] = awsner["studentName"]
                            feedback["studentId"] = awsner["studentId"]
                            # feedback["feedback"] = feedback.get("feedback", "0")
        
        # print("-----------------------------------------")
        # print(json.dumps(subQuestionResponces))
        # print("=========================================")

        # Clear previous feedbacks in the output frame
        for widget in output_frame.winfo_children():
            widget.destroy()
        
        # Display feedback in the GUI
        sub_question_notebook = ttk.Notebook(output_frame)
        sub_question_notebook.pack(fill=tk.BOTH, expand=True)

        sub_question_index = 0
        for subQuestionResponce in subQuestionResponces:
            sub_question_index += 1
                
            sub_question_frame = tk.Frame(sub_question_notebook)
            sub_question_notebook.add(sub_question_frame, text=f"{sub_question_index}")
                
            student_notebook = ttk.Notebook(sub_question_frame)
            student_notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            for feedback in subQuestionResponce.get("feedbacks", []):
                student_frame = tk.Frame(student_notebook)
                student_notebook.add(student_frame, text=feedback["studentName"])
                    
                name_label = tk.Label(student_frame, text=f"Schülername: {feedback['studentName']}", anchor='w')
                name_label.pack(fill=tk.X, padx=5, pady=(10, 2))
                    
                feedback_label = tk.Label(student_frame, text="Feedback:", anchor='w')
                feedback_label.pack(fill=tk.X, padx=5)
                feedback_text = scrolledtext.ScrolledText(student_frame, wrap=tk.WORD, width=80, height=5)
                feedback_text.insert(tk.END, feedback["feedback"])
                feedback_text.pack(fill=tk.X, padx=5, pady=2)
                    
                bewertung_label = tk.Label(student_frame, text="Bewertung:", anchor='w')
                bewertung_label.pack(fill=tk.X, padx=5)
                bewertung_entry = tk.Entry(student_frame, width=10)
                bewertung_entry.insert(0, f"{feedback['grade']}%")
                bewertung_entry.pack(fill=tk.X, padx=5, pady=(2, 10))

    #except json.JSONDecodeError:
    #    messagebox.showerror("Fehler", "Eingabedaten sind kein gültiger JSON-String.")
    #except Exception as e:
    #    messagebox.showerror("Fehler", str(e))

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
