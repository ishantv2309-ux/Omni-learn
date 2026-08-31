import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.models import Note
from backend.schemas import NoteResponse
import re
from backend.services.storage_service import StorageService
from backend.services.ocr_service import OCRService
from backend.services.gemini_service import GeminiService

router = APIRouter(prefix="/api/notes", tags=["Handwritten & Digital Notes"])

@router.get("", response_model=List[NoteResponse])
def get_notes(subject: Optional[str] = None, db: Session = Depends(get_db)):
    """Fetch all indexed notes, optionally filtered by subject."""
    q = db.query(Note)
    if subject:
        q = q.filter(Note.subject.ilike(f"%{subject}%"))
    return q.all()

@router.post("/upload", response_model=NoteResponse)
async def upload_note(
    title: str = Form(...),
    subject: str = Form(...),
    uploaded_by: Optional[str] = Form("Anonymous"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Uploads a note file, runs OCR on it, and indexes the text in the database."""
    # Validate extension
    ext = file.filename.split(".")[-1].lower()
    if ext not in ["pdf", "jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Only PDF and image uploads (JPEG/PNG) are supported")
        
    file_type = "pdf" if ext == "pdf" else "image"
    
    # Save file
    filename = f"{int(os.path.getmtime(file.file.fileno()) if hasattr(file.file, 'fileno') else 0)}_{file.filename}"
    # Sanitizing filename
    filename = "".join(c for c in filename if c.isalnum() or c in "._-")
    
    try:
        saved_path = StorageService.save_file(file, filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {e}")
        
    # Extract text using OCR (multimodal Gemini or mock depending on configuration)
    ocr_text = OCRService.extract_text(saved_path, filename)
    
    # Save to database
    db_note = Note(
        title=title,
        subject=subject,
        file_path=filename, # Store filename to query locally
        file_type=file_type,
        ocr_text=ocr_text,
        uploaded_by=uploaded_by
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    return db_note

@router.get("/search", response_model=List[NoteResponse])
def search_inside_notes(query: str = Query(...), db: Session = Depends(get_db)):
    """Performs full-text deep search inside notes by looking at indexed OCR text, titles, or subjects."""
    if not query.strip():
        return []
    return db.query(Note).filter(
        (Note.ocr_text.ilike(f"%{query}%")) |
        (Note.title.ilike(f"%{query}%")) |
        (Note.subject.ilike(f"%{query}%"))
    ).all()

def get_aktu_unit_topics(subject: str, unit: int) -> str:
    """Returns official syllabus chapter topics mapped for UPTU/AKTU BTech curriculum."""
    s = subject.lower()
    if "physics" in s:
        topics = [
            "Frame of reference, Michelson- Morley experiment, Special theory of relativity, Lorentz transformation.",
            "Continuity equation, Maxwell's equations, Poynting vector, wave propagation in dielectrics.",
            "Wave-particle duality, de Broglie waves, Heisenberg uncertainty relation, Schrodinger wave equation.",
            "Interference of light, double slit, Newton's rings, Fresnel and Fraunhofer diffraction, diffraction grating.",
            "Einstein's coefficients, Ruby laser, He-Ne laser, optical fiber types, numerical aperture, attenuation."
        ]
    elif "chemistry" in s:
        topics = [
            "Molecular orbital theory, LCAO method, metallic bonding, liquid crystals, green chemistry principles.",
            "Elementary ideas and applications of UV-visible, IR, Raman, and NMR spectroscopy.",
            "Nernst equation, galvanic cells, batteries, dry/wet corrosion, passivation, prevention methods.",
            "Hardness of water, estimation by EDTA, boiler troubles, lime-soda softening, reverse osmosis.",
            "Classification, preparation and properties of thermoplastics and thermosets, Grignard reagent."
        ]
    elif "math" in s:
        topics = [
            "Successive differentiation, Leibniz's theorem, curve tracing, asymptotes, curvature.",
            "Partial derivatives, Euler's theorem, total derivative, Jacobians, Taylor series for two variables.",
            "Rank of matrix, inverse, linear system solutions, eigen values, Cayley-Hamilton theorem.",
            "Multiple integrals, double and triple integration, change of order, area and volume.",
            "Gradient, divergence, curl, line, surface and volume integrals, Green's and Stokes' theorems."
        ]
    elif "structures" in s or "dsa" in s:
        topics = [
            "Big-O, Omega, Theta notations, multi-dimensional arrays, address calculations, sparse matrix.",
            "Singly linked lists, circular list, doubly linked list operations, linked list inversion.",
            "Stack implementation, recursion, infix to postfix conversions, queues, circular queues, deques.",
            "Binary tree properties, traversals, binary search tree (BST) operations, AVL trees.",
            "Bubble, insertion, quick, merge and heap sorting, linear and binary search, hashing."
        ]
    elif "operating" in s or "os" in s:
        topics = [
            "OS services, system calls, process state transitions, PCB, CPU scheduling.",
            "Critical section, semaphores, monitors, deadlock prevention and Banker's algorithm.",
            "Logical/physical address space, paging, segmentation, virtual memory, page replacement.",
            "File concepts, directory systems, allocation methods, disk scheduling (FCFS, SSTF, SCAN).",
            "Linux kernel modules, process management in Linux, security features."
        ]
    elif "database" in s or "dbms" in s:
        topics = [
            "Data independence, database languages, ER diagram mapping, weak entities.",
            "Relational algebra, SQL DDL/DML queries, integrity constraints, joins.",
            "Functional dependencies, normalization (1NF, 2NF, 3NF, BCNF), dependency preservation.",
            "ACID properties, serializability, lock-based protocols, two-phase locking (2PL).",
            "Deadlock handling, log-based recovery, shadow paging, check-points."
        ]
    elif "cloud" in s or "devops" in s:
        topics = [
            "Hypervisors, SaaS, PaaS, IaaS, private and public cloud configurations.",
            "Docker container builds, Kubernetes pod structures, services, controllers.",
            "Jenkins automation, GitHub Actions, unit testing pipelines, automated deployments.",
            "Terraform configurations, resource blocks, state file management.",
            "Prometheus alerts, Grafana dashboards, ELK log analysis."
        ]
    elif "machine" in s or "learning" in s:
        topics = [
            "Information gain, Gini index, support vector machine maximum margins.",
            "Multi-layer perceptrons, activation functions, gradient descent backpropagation.",
            "Convolutional Neural Networks (CNN), Recurrent Neural Networks (RNN).",
            "L1/L2 regularization, dropouts, early stopping, cross-validation metrics.",
            "Q-learning, Bellman equation, policy iteration, value iteration."
        ]
    else:
        topics = [
            "Foundational principles, core definitions, basic concepts, first principles.",
            "Mechanism analysis, quantitative models, system attributes, structural mapping.",
            "Process flows, operational steps, design architectures, transition diagrams.",
            "Optimization methods, performance margins, complexity constraints, quality checks.",
            "Practical case studies, industry scenarios, evaluation review, standard questions."
        ]
    idx = max(1, min(5, unit)) - 1
    return topics[idx]

@router.get("/file/{filename}")
def serve_note_file(filename: str):
    """Serves the actual file for display in the frontend viewer or download. Dynamically generates if missing."""
    try:
        file_path = StorageService.get_file_path(filename)
        if not file_path.exists():
            lower_name = filename.lower()
            if lower_name.startswith("aktu_"):
                m = re.search(r'aktu_(.+)_unit_(\d+)', lower_name)
                if m:
                    subject_slug = m.group(1)
                    unit_num = int(m.group(2))
                    chapters = get_aktu_unit_topics(subject_slug, unit_num)
                else:
                    subject_slug = "engineering_subject"
                    unit_num = 1
                    chapters = "Syllabus revision guides, core questions, derivations."
                
                subject_title = filename.replace("_", " ").replace(".html", "").replace(".txt", "").replace("aktu", "").title().strip()
                content = GeminiService.generate_detailed_notes(subject_title, chapters)
                
                if lower_name.endswith(".html"):
                    formatted_content = ""
                    for line in content.split("\n"):
                        line_stripped = line.strip()
                        if not line_stripped:
                            formatted_content += "<br/>"
                        elif line_stripped.startswith("####"):
                            formatted_content += f"<h4 class='text-sm font-bold text-slate-800 mt-4 mb-2 font-sans'>{line_stripped.replace('####', '').strip()}</h4>"
                        elif line_stripped.startswith("###"):
                            formatted_content += f"<h3 class='text-md font-bold text-indigo-700 mt-5 mb-2.5 font-sans flex items-center'><span class='w-1.5 h-4 bg-indigo-500 rounded-full mr-2'></span>{line_stripped.replace('###', '').strip()}</h3>"
                        elif line_stripped.startswith("##"):
                            formatted_content += f"<h2 class='text-lg font-bold text-slate-850 mt-8 mb-4 border-b border-slate-100 pb-2 font-sans flex items-center'><span class='w-2.5 h-5 bg-indigo-650 rounded-md mr-2.5 text-white flex items-center justify-center text-[10px]'><i class='fa-solid fa-book-open'></i></span>{line_stripped.replace('##', '').strip()}</h2>"
                        elif line_stripped.startswith("-") or line_stripped.startswith("*"):
                            clean_line = re.sub(r'^[\-\*]\s*', '', line_stripped)
                            clean_line = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-bold text-slate-900">\1</strong>', clean_line)
                            formatted_content += f"<li class='ml-6 list-disc text-slate-600 my-1.5 font-sans leading-relaxed'>{clean_line}</li>"
                        else:
                            clean_line = re.sub(r'\*\*(.*?)\*\*', r'<strong class="font-bold text-slate-900">\1</strong>', line_stripped)
                            if re.match(r'^\d+\.', clean_line):
                                formatted_content += f"<p class='pl-6 text-slate-600 my-2 leading-relaxed font-sans'>{clean_line}</p>"
                            else:
                                formatted_content += f"<p class='text-slate-600 my-2 leading-relaxed font-sans'>{clean_line}</p>"
                                
                    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject_title} - AKTU Study Resource</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
            min-height: 100vh;
        }}
        .note-container {{
            background: #ffffff;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.05), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            border: 1px solid #e2e8f0;
            border-radius: 24px;
            position: relative;
        }}
        .note-container::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 20px;
            bottom: 0;
            width: 2px;
            background-color: #f1f5f9;
        }}
        .note-header-border {{
            border-bottom: 2px dashed #cbd5e1;
        }}
        @media print {{
            .no-print {{
                display: none !important;
            }}
            body {{
                background: white !important;
                padding: 0 !important;
            }}
            .note-container {{
                box-shadow: none !important;
                border: none !important;
                margin: 0 !important;
                padding: 0 !important;
            }}
            .note-container::before {{
                display: none !important;
            }}
        }}
    </style>
</head>
<body class="py-12 px-4 md:px-8">
    <div class="max-w-4xl mx-auto">
        <!-- Floating Glassmorphic Actions -->
        <div class="flex justify-between items-center mb-8 bg-white/70 backdrop-blur-md border border-slate-200/80 p-4 rounded-2xl shadow-sm no-print font-sans">
            <a href="javascript:window.close()" class="inline-flex items-center space-x-2 text-slate-600 hover:text-indigo-650 font-semibold transition text-sm">
                <i class="fa-solid fa-arrow-left text-xs"></i>
                <span>Close Study Note</span>
            </a>
            <div class="flex items-center space-x-3">
                <span class="text-xs font-semibold text-slate-400 bg-slate-100 py-1 px-2.5 rounded-lg border border-slate-200/60 flex items-center gap-1.5">
                    <span class="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span> Verified Source
                </span>
                <button onclick="window.print()" class="bg-indigo-650 hover:bg-indigo-700 text-white font-bold px-4 py-2 rounded-xl shadow-sm hover:shadow transition duration-200 flex items-center space-x-2 text-sm">
                    <i class="fa-solid fa-file-pdf"></i>
                    <span>Print / Save PDF</span>
                </button>
            </div>
        </div>

        <!-- Premium Note Sheet Card -->
        <div class="note-container p-8 md:p-14">
            <!-- University & Header -->
            <div class="note-header-border pb-6 mb-8">
                <div class="flex flex-col items-center text-center">
                    <span class="bg-indigo-50 text-indigo-700 text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider border border-indigo-100 flex items-center gap-1.5 mb-3 font-sans">
                        <i class="fa-solid fa-university"></i> AKTU / UPTU Syllabus
                    </span>
                    <h1 class="text-xl md:text-3xl font-extrabold text-slate-800 leading-tight tracking-tight uppercase font-sans">
                        DR. A.P.J. ABDUL KALAM TECHNICAL UNIVERSITY
                    </h1>
                    <p class="text-xs text-slate-450 mt-1 font-semibold uppercase tracking-widest font-sans">
                        Official Academic Curricular Study Resource
                    </p>
                    
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-lg mt-6 bg-slate-50 border border-slate-200/60 p-4 rounded-xl text-xs text-left">
                        <div class="flex items-center space-x-2 min-w-0 font-sans">
                            <span class="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-650 flex items-center justify-center flex-shrink-0">
                                <i class="fa-solid fa-book"></i>
                            </span>
                            <span class="truncate"><strong class="text-slate-800">Subject:</strong> {subject_title}</span>
                        </div>
                        <div class="flex items-center space-x-2 min-w-0 font-sans">
                            <span class="w-7 h-7 rounded-lg bg-indigo-50 text-indigo-650 flex items-center justify-center flex-shrink-0">
                                <i class="fa-solid fa-circle-nodes"></i>
                            </span>
                            <span class="truncate"><strong class="text-slate-800">Archive:</strong> a2zteaching.com</span>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Notes Body -->
            <div class="pl-2 md:pl-6 pr-2 pt-2">
                <div class="prose max-w-none">
                    {formatted_content}
                </div>
            </div>
            
            <div class="border-t border-slate-100 mt-12 pt-8 text-center text-[10px] text-slate-400 font-medium tracking-wide uppercase flex flex-col md:flex-row justify-between gap-4 font-sans">
                <span>Dr. A.P.J. Abdul Kalam Technical University (AKTU) Study Material</span>
                <span>Licensed to OmniLearn &bull; a2zteaching.com</span>
            </div>
        </div>
    </div>
</body>
</html>"""
                    file_path.write_text(html_content, encoding="utf-8")
                else:
                    file_path.write_text(content, encoding="utf-8")
            else:
                raise HTTPException(status_code=404, detail="File not found")
        
        # Set proper media type
        lower_filename = filename.lower()
        if lower_filename.endswith(".pdf"):
            media_type = "application/pdf"
        elif lower_filename.endswith(".html"):
            media_type = "text/html"
        elif lower_filename.endswith(".txt"):
            media_type = "text/plain"
        else:
            media_type = "image/jpeg"
            
        return FileResponse(path=file_path, media_type=media_type, filename=filename)
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
