import os
from backend import config

class OCRService:
    @staticmethod
    def extract_text(file_path: str, filename: str) -> str:
        """Extracts text from a note (PDF or image).
        Uses Gemini's multimodal capacity in production or returns realistic mock text.
        """
        if config.is_gemini_mocked():
            return OCRService._get_mock_ocr_text(filename)
            
        try:
            from google.genai import types
            from backend.services.gemini_service import GeminiService
            
            client = GeminiService.get_client()
            if not client:
                return OCRService._get_mock_ocr_text(filename)
            
            # Read file bytes
            with open(file_path, "rb") as f:
                file_bytes = f.read()
                
            # Determine mime type
            mime_type = "application/pdf" if filename.lower().endswith(".pdf") else "image/jpeg"
            
            prompt = (
                "You are an expert educational OCR engine. Extract all readable text, handwritten "
                "notes, formulas, drawings description, and structures from this document. "
                "Output ONLY the extracted text and formulas clearly."
            )
            
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=[
                    types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=mime_type,
                    ),
                    prompt
                ],
                config=types.GenerateContentConfig(
                    temperature=0.0
                )
            )
            
            return response.text if response.text else ""
            
        except Exception as e:
            print(f"OCR Error using Gemini API: {e}. Falling back to mock text.")
            return OCRService._get_mock_ocr_text(filename)

    @staticmethod
    def _get_mock_ocr_text(filename: str) -> str:
        """Returns realistic academic text contents for mock searches."""
        fn = filename.lower()
        if "newton" in fn or "force" in fn or "motion" in fn or "physics" in fn:
            return """
            Handwritten Note: Newton's Laws of Motion
            - First Law (Law of Inertia): An object remains at rest or in uniform motion unless acted upon by an external net force.
              Formula: If F_net = 0, then dv/dt = 0.
            - Second Law: The acceleration of an object is directly proportional to the net force acting on it and inversely proportional to its mass.
              Formula: F = m * a  (Vector equation: F = dp/dt)
            - Third Law: For every action, there is an equal and opposite reaction.
              Formula: F_AB = -F_BA.
            Examples: A book resting on a table, rocket propulsion, recoil of a gun.
            Note: Inertial frame of reference is required for Newton's laws to hold.
            """
        elif "list" in fn or "pointer" in fn or "datastructure" in fn or "array" in fn:
            return """
            Handwritten Note: Linked List Inversion (Singly Linked List)
            Problem: Reverse a singly linked list.
            Algorithm (Iterative Approach):
            1. Initialize three pointers: prev = NULL, curr = head, next = NULL.
            2. Iterate through the list. In each step:
               next = curr->next
               curr->next = prev
               prev = curr
               curr = next
            3. Reset head to prev.
            Complexity: Time: O(N) | Space: O(1)
            Recursive Approach:
            Node* reverse(Node* head) {
               if (head == NULL || head->next == NULL) return head;
               Node* rest = reverse(head->next);
               head->next->next = head;
               head->next = NULL;
               return rest;
            }
            """
        elif "calculus" in fn or "integration" in fn or "math" in fn:
            return """
            Handwritten Note: Integration Techniques & Calculus
            - Integration by parts: Integral of u dv = u*v - Integral of v du.
            - Substitution Rule: Integral of f(g(x))*g'(x) dx = Integral of f(u) du where u = g(x).
            - Trigonometric substitutions:
              For sqrt(a^2 - x^2), let x = a*sin(theta).
              For sqrt(a^2 + x^2), let x = a*tan(theta).
              For sqrt(x^2 - a^2), let x = a*sec(theta).
            - Applications: Area under curve, volume of solids of revolution.
            """
        else:
            return f"""
            Handwritten Note: General Study Guide
            Document name: {filename}
            Subject: General Studies & Exam Prep.
            Key Concepts: Core summaries, textbook references, and exam topics.
            Please review the roadmap for prerequisites.
            """
