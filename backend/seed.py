import os
from pathlib import Path
from sqlalchemy.orm import Session
from backend.database import engine, Base, SessionLocal
from backend.models import PYQ, Note, Topic, SearchCache
from backend.config import STORAGE_DIR

def seed_database():
    # 1. Create all database tables
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")
    
    db: Session = SessionLocal()
    
    try:
        # Clear existing data to make seed repeatable
        db.query(PYQ).delete()
        db.query(Note).delete()
        db.query(Topic).delete()
        db.query(SearchCache).delete()
        db.commit()
        print("Existing database tables cleared.")
        
        # 2. Seed Mock Note Files on disk
        notes_data = [
            {
                "title": "Newton's Laws of Motion - Physics Note",
                "subject": "Physics",
                "filename": "newtons_laws_notes.txt",
                "file_type": "text",
                "uploaded_by": "Aditya Sharma (IIT-B)",
                "ocr_text": """
                =========================================
                 HANDWRITTEN PHYSICS NOTES: LAWS OF MOTION
                =========================================
                Author: Aditya Sharma
                Topic: Classical Mechanics - Force & Motion
                
                - Isaac Newton's three laws describe mechanical motion:
                  
                  [1] LAW OF INERTIA (1st Law)
                      Every object continues in its state of rest or uniform motion 
                      unless compelled to change by forces impressed upon it.
                      - If F_net = 0 => a = 0 (velocity is constant)
                      - Inertia depends directly on mass (more mass = more inertia).
                  
                  [2] FUNDAMENTAL LAW (2nd Law)
                      The rate of change of momentum is proportional to the net force applied.
                      - Formula: F = dp/dt = d(mv)/dt = m * a (for constant mass)
                      - Units: Newton (N) = kg * m / s^2.
                      - Practice point: Always draw Free Body Diagrams (FBD)!
                  
                  [3] ACTION-REACTION (3rd Law)
                      To every action there is always an opposed and equal reaction.
                      - F_AB = - F_BA (forces occur in pairs)
                      - Example: Walking. Foot pushes ground backward (Action), ground pushes foot forward (Reaction).
                      
                - Inclined Planes & Friction:
                  - Normal force on incline: N = m * g * cos(theta)
                  - Parallel force down incline: F_p = m * g * sin(theta)
                  - Friction: f = mu * N = mu * m * g * cos(theta)
                =========================================
                """
            },
            {
                "title": "Singly Linked List Inversion - DSA Notes",
                "subject": "Computer Science",
                "filename": "linked_list_reversal_notes.txt",
                "file_type": "text",
                "uploaded_by": "Rohit Verma (NSUT)",
                "ocr_text": """
                =========================================
                 HANDWRITTEN DATA STRUCTURE NOTES: LINKED LISTS
                =========================================
                Topic: Singly Linked List Inversion / Reversal
                Author: Rohit Verma
                
                Problem Statement:
                Given the head pointer of a Singly Linked List, reverse it in-place.
                
                1. ITERATIVE METHOD
                   - We need 3 pointers to perform reversal without losing references:
                     * prev (tracks reversed part - initial NULL)
                     * curr (tracks current traversal node - initial head)
                     * next (stores the next node temporarily)
                   
                   Code:
                   Node* reverse(Node* head) {
                       Node* prev = NULL;
                       Node* curr = head;
                       Node* next = NULL;
                       while (curr != NULL) {
                           next = curr->next;  // save next node
                           curr->next = prev;  // reverse pointer direction
                           prev = curr;        // advance prev
                           curr = next;        // advance curr
                       }
                       return prev; // new head of reversed list
                   }
                   
                   Time Complexity: O(N) since we visit every node exactly once.
                   Space Complexity: O(1) auxiliary space (only pointers used).
                   
                2. RECURSIVE METHOD
                   - Solve for rest of list, then make head's next node point back to head.
                   Code:
                   Node* reverseRecursive(Node* head) {
                       if (head == NULL || head->next == NULL) return head;
                       Node* rest = reverseRecursive(head->next);
                       head->next->next = head;
                       head->next = NULL;
                       return rest;
                   }
                   Time Complexity: O(N) | Space Complexity: O(N) for recursion call stack.
                =========================================
                """
            },
            {
                "title": "Calculus: Integration by Parts & Substitution",
                "subject": "Mathematics",
                "filename": "calculus_integration_notes.txt",
                "file_type": "text",
                "uploaded_by": "Prof. R. Sen (IISER)",
                "ocr_text": """
                =========================================
                 LECTURE NOTE: INTEGRATION TECHNIQUES
                =========================================
                Subject: Calculus / Mathematics
                Topic: Methods of Integration (Indefinite)
                
                1. INTEGRATION BY SUBSTITUTION (U-Substitution)
                   - If u = g(x), then du = g'(x)dx.
                   - Integral of f(g(x)) * g'(x) dx = Integral of f(u) du.
                   - Example: Integral of x * cos(x^2) dx.
                     Let u = x^2 => du = 2x dx => x dx = du/2.
                     Res: 1/2 * Integral of cos(u) du = 1/2 * sin(u) + C = 1/2 * sin(x^2) + C.
                     
                2. INTEGRATION BY PARTS (IBP)
                   - Formula: Integral of u dv = u * v - Integral of v du.
                   - Choice of u is guided by the ILATE rule:
                     * I : Inverse trigonometric functions
                     * L : Logarithmic functions
                     * A : Algebraic functions
                     * T : Trigonometric functions
                     * E : Exponential functions
                   - Example: Integral of ln(x) dx.
                     Let u = ln(x) => du = 1/x dx.
                     Let dv = dx => v = x.
                     Res: ln(x)*x - Integral of x * (1/x) dx = x * ln(x) - x + C.
                =========================================
                """
            }
        ]
        
        for note in notes_data:
            # Write note text to storage dir
            note_path = STORAGE_DIR / note["filename"]
            with open(note_path, "w") as f:
                f.write(note["ocr_text"].strip())
                
            db_note = Note(
                title=note["title"],
                subject=note["subject"],
                file_path=note["filename"],
                file_type=note["file_type"],
                ocr_text=note["ocr_text"].strip(),
                uploaded_by=note["uploaded_by"]
            )
            db.add(db_note)
            
        print("Note files saved and database records seeded.")

        # 3. Seed Mock Previous Year Questions (PYQs)
        pyq_data = [
            PYQ(
                question_text="Derive the expression for the acceleration of a block of mass 'm' sliding down a rough inclined plane making an angle 'theta' with the horizontal, where the coefficient of static friction is 'mu'. Draw a clear Free Body Diagram (FBD).",
                year=2025,
                exam_name="JEE Main Physics Paper 1",
                board_university="NTA",
                subject="Physics",
                difficulty="Hard",
                topic_tags="newton, force, friction, incline, laws of motion"
            ),
            PYQ(
                question_text="A man of mass 70 kg stands on a weighing scale in a lift. What would be the scale reading if the lift is (a) moving upwards with uniform speed 5 m/s, (b) accelerating downwards at 3 m/s^2, (c) accelerating upwards at 2 m/s^2? Take g = 10 m/s^2.",
                year=2024,
                exam_name="CBSE Class 11 Physics Term Exam",
                board_university="CBSE",
                subject="Physics",
                difficulty="Medium",
                topic_tags="newton, laws of motion, force, lift, gravity"
            ),
            PYQ(
                question_text="State Newton's third law of motion. Explain why a horse cannot pull a cart in empty space. Discuss action-reaction pairs in detail.",
                year=2023,
                exam_name="ICSE Board Class 10 Physics",
                board_university="ICSE",
                subject="Physics",
                difficulty="Easy",
                topic_tags="newton, force, third law, laws of motion"
            ),
            PYQ(
                question_text="Write a function in C/C++ or Python to reverse a Singly Linked List iteratively. Analyze its time and space complexity, explaining why the space complexity is O(1).",
                year=2025,
                exam_name="Data Structures Semester Exam",
                board_university="Mumbai University",
                subject="Computer Science",
                difficulty="Medium",
                topic_tags="linked list, reverse, pointers, iterative"
            ),
            PYQ(
                question_text="Explain the recursive method to reverse a singly linked list. Show the call stack diagram for a list containing 3 nodes: A -> B -> C -> NULL. What are the space implications?",
                year=2024,
                exam_name="Computer Science Paper 2 (Algorithms)",
                board_university="Delhi University",
                subject="Computer Science",
                difficulty="Hard",
                topic_tags="linked list, reverse, pointers, recursive, algorithms"
            ),
            PYQ(
                question_text="What is a loop in a linked list? Write an algorithm to detect and remove a loop in a singly linked list. Explain the mathematical logic behind Floyd's Cycle Detection Algorithm.",
                year=2023,
                exam_name="Gate CS Exam",
                board_university="IIT Kanpur",
                subject="Computer Science",
                difficulty="Hard",
                topic_tags="linked list, loop, floyd, cycle detection, pointers"
            ),
            PYQ(
                question_text="Integrate the function x^3 * log(x) with respect to x using the integration by parts method. State the ILATE rule.",
                year=2024,
                exam_name="CBSE Class 12 Mathematics Board Exam",
                board_university="CBSE",
                subject="Mathematics",
                difficulty="Medium",
                topic_tags="calculus, integration, parts, math"
            ),
            PYQ(
                question_text="Evaluate the integral of dx / (x * sqrt(x^2 - a^2)) using appropriate trigonometric substitution. Show all steps of variable substitution.",
                year=2023,
                exam_name="Engineering Mathematics-I",
                board_university="VTU Karnataka",
                subject="Mathematics",
                difficulty="Hard",
                topic_tags="calculus, integration, substitution, math"
            )
        ]
        
        for pyq in pyq_data:
            db.add(pyq)
            
        db.commit()
        print("Previous Year Questions (PYQs) database records seeded.")
        print("Database seeding completed successfully.")
        
    except Exception as e:
        db.rollback()
        print(f"Seeding failed: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
