import random
import time
import pyttsx3
import requests
import matplotlib.pyplot as plt
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from io import BytesIO
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# NASA API for image and fact
NASA_API_URL = "https://api.nasa.gov/planetary/apod?api_key=vf8gG0BWhAdbIcraaghxiAB1MAkzcDh3cykBuI5d"

def get_apod(api_key):
    url = f"https://api.nasa.gov/planetary/apod?api_key={api_key}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching APOD data: {e}")
        return None

def get_nasa_images(query, page=1):
    url = f"https://images-api.nasa.gov/search?q={query}&media_type=image&page={page}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['collection']['items']
    except requests.exceptions.RequestException as e:
        print(f"Error fetching NASA images: {e}")
        return []

def generate_quiz(api_key):
    apod_data = get_apod(api_key)
    if not apod_data:
        print("Error fetching APOD data. Exiting quiz generation.")
        return []
    
    image_questions = []
    
    # APOD-based question
    apod_question = {
        "question": f"What is the title of NASA's Astronomy Picture of the Day (APOD) for today?",
        "explanation": f"{apod_data['explanation']}",
        "options": [apod_data['title'], "A distant galaxy", "A supernova remnant", "A space shuttle launch"],
        "answer": apod_data['title'],
        "image": apod_data['url']
    }
    image_questions.append(apod_question)
    
    # NASA Image API-based questions
    queries = ["galaxy", "nebula", "moon", "mars", "black hole","milkyway galaxy","sun","earth","moon","jupiter","invention","telescope"]
    for query in queries:
        images = get_nasa_images(query)
        if images:
            img = random.choice(images)
            title = img['data'][0]['title']
            
            question = {
                "question": f"What is shown in this NASA image?",
                "explanation": f"{img['data'][0]['description']}",
                "options": [title, "A star system", "A planetary ring", "An asteroid belt"],
                "answer": title,
                "image": img['links'][0]['href']
            }
            image_questions.append(question)
    
    return image_questions

# Initialize Text-to-Speech Engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("NASA Quiz")
        self.name = ""
        self.age = 0
        self.questions_answered = 0
        self.points = 0
        self.highest_score = 0
        self.total_questions = 0
        self.scores = []
        self.quiz_questions = generate_quiz("vf8gG0BWhAdbIcraaghxiAB1MAkzcDh3cykBuI5d")
        self.ask_for_details()

    def ask_for_details(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        frame = Frame(self.root)
        frame.pack(pady=20)
        
        Label(frame, text="Enter your details", font=("Arial", 14)).grid(row=0, columnspan=2, pady=10)
        
        Label(frame, text="Name:").grid(row=1, column=0, sticky=W)
        self.name_entry = Entry(frame)
        self.name_entry.grid(row=1, column=1)
        
        Label(frame, text="Age:").grid(row=2, column=0, sticky=W)
        self.age_entry = Entry(frame)
        self.age_entry.grid(row=2, column=1)
        
        Label(frame, text="Number of Questions:").grid(row=3, column=0, sticky=W)
        self.questions_entry = Entry(frame)
        self.questions_entry.grid(row=3, column=1)
        
        Button(frame, text="Start Quiz", command=self.start_quiz).grid(row=4, columnspan=2, pady=10)
    
    def start_quiz(self):
        self.name = self.name_entry.get()
        self.age = int(self.age_entry.get())
        self.total_questions = min(int(self.questions_entry.get()), len(self.quiz_questions))
        speak(f"Hello {self.name}, Welcome to the NASA Quiz!")
        self.show_countdown()

    def show_countdown(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        countdown_label = Label(self.root, text="Starting in 3...", font=("Arial", 14))
        countdown_label.pack()
        self.root.update()
        time.sleep(1)
        countdown_label.config(text="Starting in 2...")
        self.root.update()
        time.sleep(1)
        countdown_label.config(text="Starting in 1...")
        self.root.update()
        time.sleep(1)
        countdown_label.config(text="Go!")
        self.root.update()
        time.sleep(1)
        countdown_label.pack_forget()
        self.ask_question()

    def ask_question(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        if self.questions_answered >= self.total_questions:
            self.end_game()
            return
        
        question_data = self.quiz_questions[self.questions_answered]
        question_label = Label(self.root, text=question_data["question"], wraplength=400, font=("Arial", 12))
        question_label.pack()
        speak(question_data["question"])
        
        # Randomize the answer options
        options = question_data["options"]
        random.shuffle(options)  # Shuffle options so the correct answer is not always first
        
        if "image" in question_data and question_data["image"]:
            try:
                img_data = requests.get(question_data["image"]).content
                img = Image.open(BytesIO(img_data))
                img.thumbnail((300, 300))
                img_tk = ImageTk.PhotoImage(img)
                image_label = Label(self.root, image=img_tk)
                image_label.image = img_tk
                image_label.pack()
            except Exception as e:
                print(f"Error displaying image: {e}")
        
        self.options_buttons = []
        for option in options:
            btn = Button(self.root, text=option, command=lambda opt=option: self.check_answer(opt, question_data["answer"]))
            btn.pack()
            self.options_buttons.append(btn)

    def check_answer(self, selected, correct_answer):
        self.questions_answered += 1
        explanation = self.quiz_questions[self.questions_answered - 1]["explanation"]

        if selected == correct_answer:
            self.points += 10
            messagebox.showinfo("Correct!", f"That's the correct answer!\n\nExplanation:\n{explanation}")
        else:
            self.points -= 5
            messagebox.showinfo("Incorrect", f"Sorry, the correct answer was: {correct_answer}\n\nExplanation:\n{explanation}")
        
        # Update highest score
        if self.points > self.highest_score:
            self.highest_score = self.points
        
        self.scores.append(self.points)
        self.ask_question()

    def end_game(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        result_label = Label(self.root, text=f"Game Over! {self.name}, your score: {self.points}", font=("Arial", 14))
        result_label.pack()
        speak(f"Game Over! Your final score is {self.points}")
        self.show_graph()
    
    def show_graph(self):
        # Creating parabola-like curve
        x = np.arange(0, len(self.scores))
        y = np.array(self.scores)
        
        # Parabola fitting (quadratic curve)
        p = np.polyfit(x, y, 2)
        parabola_y = np.polyval(p, x)
        
        # Creating figure and plot
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(x, parabola_y, label="Parabola Fit", color='r', linestyle='--')
        ax.scatter(x, y, color='b', label="Scores")
        
        # Mark highest score on graph
        ax.axhline(self.highest_score, color='g', linestyle='-.', label=f"Highest Score: {self.highest_score}")
        
        ax.set_xlabel("Question Number")
        ax.set_ylabel("Score")
        ax.set_title("Quiz Score Progression")
        ax.legend()
        ax.grid()

        # Embed the plot in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().pack(pady=20)
        canvas.draw()

# Main GUI setup
root = Tk()
app = QuizApp(root)
root.mainloop()
