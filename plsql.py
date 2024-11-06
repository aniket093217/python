import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3

class OnlineVotingSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Voting System")
        self.root.geometry("1000x700")
        self.password = "pankaj@123"  # You can set your desired password here

        self.create_database()
        self.create_widgets()

    def create_database(self):
        conn = sqlite3.connect('online_voting_system.db')
        cursor = conn.cursor()

        # Create voters table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            has_voted BOOLEAN DEFAULT FALSE
        )
        ''')

        # Create candidates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            party TEXT NOT NULL
        )
        ''')

        # Create votes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            FOREIGN KEY (voter_id) REFERENCES voters(id),
            FOREIGN KEY (candidate_id) REFERENCES candidates(id)
        )
        ''')

        # Insert candidates if they don't exist
        candidates = [
            ('Pankaj', 'Independent'),
            ('Ashish', 'Democratic'),
            ('Suyash', 'Republican'),
            ('Prabhakar', 'Liberal'),
        ]

        for name, party in candidates:
            cursor.execute("SELECT * FROM candidates WHERE name = ?", (name,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO candidates (name, party) VALUES (?, ?)", (name, party))

        conn.commit()
        conn.close()

    def create_widgets(self):
        # Title
        title = tk.Label(self.root, text="Online Voting System", font=("Arial", 24), bg="blue", fg="white")
        title.pack(pady=10, )

        # Voter Registration Section
        self.voter_frame = tk.Frame(self.root, bg="lightgray")
        self.voter_frame.pack(pady=20, padx=20, )

        tk.Label(self.voter_frame, text="Name:", bg="lightgray").grid(row=0, column=0)
        self.voter_name = tk.Entry(self.voter_frame)
        self.voter_name.grid(row=0, column=1)

        tk.Label(self.voter_frame, text="Email:", bg="lightgray").grid(row=1, column=0)
        self.voter_email = tk.Entry(self.voter_frame)
        self.voter_email.grid(row=1, column=1)

        tk.Button(self.voter_frame, text="Register Voter", command=self.register_voter, bg="green", fg="white").grid(row=2, columnspan=2)

        # Voting Section
        self.vote_frame = tk.Frame(self.root, bg="lightyellow")
        self.vote_frame.pack(pady=20, padx=20, )

        tk.Label(self.vote_frame, text="Select Candidate:", bg="lightyellow").grid(row=0, column=0)
        self.candidate_combobox = ttk.Combobox(self.vote_frame)
        self.candidate_combobox.grid(row=0, column=1)

        tk.Button(self.vote_frame, text="Vote", command=self.cast_vote, bg="green", fg="white").grid(row=1, columnspan=2)

        # Display Results Button with password
        tk.Button(self.root, text="Show Results", command=self.check_password_results, bg="purple", fg="white").pack(pady=20)

        # View Voters Button with password
        tk.Button(self.root, text="View Voters", command=self.check_password_voters, bg="purple", fg="white").pack(pady=10)

        # Delete Voter Button with password
        tk.Button(self.root, text="Delete Voter Data", command=self.check_password_delete_voter, bg="red", fg="white").pack(pady=10)

        # Delete All Data Button with password
        tk.Button(self.root, text="Delete All Data", command=self.check_password_delete_all_data, bg="red", fg="white").pack(pady=10)

        self.populate_candidates()

    def register_voter(self):
        name = self.voter_name.get().strip()
        email = self.voter_email.get().strip()

        if not name or not email:
            messagebox.showerror("Error", "All fields are required!")
            return

        conn = sqlite3.connect('online_voting_system.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO voters (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
            messagebox.showinfo("Success", "Voter registered successfully!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This email is already registered!")
        finally:
            conn.close()
            self.voter_name.delete(0, tk.END)

    def populate_candidates(self):
        conn = sqlite3.connect('online_voting_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates")
        candidates = cursor.fetchall()
        conn.close()

        self.candidate_combobox['values'] = [f"{candidate[0]}: {candidate[1]} ({candidate[2]})" for candidate in candidates]

    def cast_vote(self):
        selected_candidate = self.candidate_combobox.get()

        if not selected_candidate:
            messagebox.showerror("Error", "You must select a candidate!")
            return

        candidate_id = int(selected_candidate.split(':')[0])
        email = self.voter_email.get().strip()

        if not email:
            messagebox.showerror("Error", "You must enter your registered email to cast your vote!")
            return

        conn = sqlite3.connect('online_voting_system.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, has_voted FROM voters WHERE email = ?", (email,))
        voter = cursor.fetchone()

        if voter is None:
            messagebox.showerror("Error", "You need to register first!")
            conn.close()
            return

        voter_id, has_voted = voter

        if has_voted:
            messagebox.showerror("Error", "You have already voted!")
            conn.close()
            return

        cursor.execute("INSERT INTO votes (voter_id, candidate_id) VALUES (?, ?)", (voter_id, candidate_id))
        cursor.execute("UPDATE voters SET has_voted = TRUE WHERE id = ?", (voter_id,))
        conn.commit()

        cursor.execute("SELECT name, party FROM candidates WHERE id = ?", (candidate_id,))
        candidate = cursor.fetchone()
        messagebox.showinfo("Vote Cast", f"You voted for {candidate[0]} ({candidate[1]}).")

        conn.close()
        self.candidate_combobox.set('')

    def check_password_results(self):
        self.prompt_password(self.show_results)

    def check_password_voters(self):
        self.prompt_password(self.view_voters)

    def check_password_delete_voter(self):
        self.prompt_password(self.delete_voter)

    def check_password_delete_all_data(self):
        self.prompt_password(self.delete_all_data)

    def prompt_password(self, success_callback):
        password_window = tk.Toplevel(self.root)
        password_window.title("Enter Password")
        password_window.geometry("300x100")

        tk.Label(password_window, text="Enter Password:").pack(pady=10)
        password_entry = tk.Entry(password_window, show="*")
        password_entry.pack()

        def check_password():
            if password_entry.get() == self.password:
                password_window.destroy()
                success_callback()
            else:
                messagebox.showerror("Error", "Incorrect password!")
                password_window.destroy()

        tk.Button(password_window, text="Submit", command=check_password).pack(pady=10)

    def show_results(self):
        conn = sqlite3.connect('online_voting_system.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT candidates.name, candidates.party, COUNT(votes.id) AS vote_count
        FROM candidates
        LEFT JOIN votes ON candidates.id = votes.candidate_id
        GROUP BY candidates.id
        ''')
        
        results = cursor.fetchall()
        conn.close()

        results_window = tk.Toplevel(self.root)
        results_window.title("Voting Results")
        results_window.geometry("400x300")

        if results:
            for idx, (name, party, count) in enumerate(results):
                tk.Label(results_window, text=f"{name} ({party}): {count} votes").pack()
        else:
            tk.Label(results_window, text="No votes have been cast yet.").pack()

    def view_voters(self):
        conn = sqlite3.connect('online_voting_system.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM voters")
        voters = cursor.fetchall()
        conn.close()

        voters_window = tk.Toplevel(self.root)
        voters_window.title("Registered Voters")
        voters_window.geometry("400x300")

        for voter in voters:
            tk.Label(voters_window, text=f"ID: {voter[0]}, Name: {voter[1]}, Email: {voter[2]}, Voted: {voter[3]}").pack()

    def delete_voter(self):
        delete_window = tk.Toplevel(self.root)
        delete_window.title("Delete Voter")
        delete_window.geometry("300x200")

        tk.Label(delete_window, text="Enter Voter Email:").pack(pady=10)
        delete_email = tk.Entry(delete_window)
        delete_email.pack()

        def confirm_delete():
            email = delete_email.get().strip()
            if not email:
                messagebox.showerror("Error", "Please enter an email!")
                return

            conn = sqlite3.connect('online_voting_system.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM voters WHERE email = ?", (email,))
            conn.commit()
            if cursor.rowcount > 0:
                messagebox.showinfo("Success", "Voter deleted successfully!")
            else:
                messagebox.showerror("Error", "No voter found with that email!")
            conn.close()
            delete_window.destroy()

        tk.Button(delete_window, text="Delete Voter", command=confirm_delete).pack(pady=10)

    def delete_all_data(self):
        result = messagebox.askyesno("Confirmation", "Are you sure you want to delete all data?")
        if result:
            conn = sqlite3.connect('online_voting_system.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM voters")
            cursor.execute("DELETE FROM votes")
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "All data has been deleted!")

root = tk.Tk()
app = OnlineVotingSystem(root)
root.mainloop()

