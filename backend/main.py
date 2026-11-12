"""SkillPath AI learning API starter. Local demo backend; add verified auth before deployment."""
from __future__ import annotations
import os, random, json
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, String, Integer, Boolean, DateTime, Text, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./skillpath.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
Session = sessionmaker(engine, expire_on_commit=False)
app = FastAPI(title="SkillPath AI API", version="0.1.0", description="Deterministic Python assessment and roadmap API")
app.add_middleware(CORSMiddleware, allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:8000").split(","), allow_methods=["GET", "POST", "PATCH"], allow_headers=["Content-Type", "Authorization"])

class Base(DeclarativeBase): pass
class Profile(Base):
    __tablename__ = "user_profiles"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), default="Learner")
    career: Mapped[str] = mapped_column(String(80), default="AI/ML Engineer")
    skill: Mapped[str] = mapped_column(String(50), default="Python")
    level: Mapped[str] = mapped_column(String(30), default="Beginner")
    preferences: Mapped[str] = mapped_column(Text, default="{}")
class Assessment(Base):
    __tablename__ = "assessments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("user_profiles.id"), index=True)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    answers: Mapped[str] = mapped_column(Text, default="[]")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
class Milestone(Base):
    __tablename__ = "roadmap_milestones"
    id: Mapped[str] = mapped_column(String(80), primary_key=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("user_profiles.id"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    phase: Mapped[str] = mapped_column(String(100))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
Base.metadata.create_all(engine)

TOPICS = ["Python Fundamentals", "Conditionals & Loops", "Functions", "Data Structures", "Problem Solving", "Debugging"]
QUESTIONS = [
 {"id":"v1","topic":0,"difficulty":1,"prompt":"Which name is a valid Python variable name?","options":["user-name","2users","user_name","class"],"answer":2,"explanation":"Names can include letters, digits, and underscores, cannot start with digits, and cannot be reserved words."},
 {"id":"v2","topic":0,"difficulty":2,"prompt":"What is the type of 3.0?","options":["int","float","str","decimal"],"answer":1,"explanation":"A numeric literal with a decimal point is a float."},
 {"id":"l1","topic":1,"difficulty":1,"prompt":"How many times does for i in range(3) run?","options":["2","3","4","1"],"answer":1,"explanation":"range(3) produces three values: 0, 1, and 2."},
 {"id":"l2","topic":1,"difficulty":2,"prompt":"What does total become after adding 2, 4, and 6?","options":["10","12","246","6"],"answer":1,"explanation":"The sum is 12."},
 {"id":"f1","topic":2,"difficulty":1,"prompt":"Which keyword sends a value back from a function?","options":["yield","return","print","send"],"answer":1,"explanation":"return provides a function's result to its caller."},
 {"id":"f2","topic":2,"difficulty":2,"prompt":"What is one benefit of a pure function?","options":["It changes global values","Same input gives same output without side effects","It always prints","It takes one argument"],"answer":1,"explanation":"Pure functions are predictable and have no observable side effects."},
 {"id":"d1","topic":3,"difficulty":1,"prompt":"Which brackets create a Python list?","options":["{}","()","[]","<>"],"answer":2,"explanation":"Square brackets create a list."},
 {"id":"d2","topic":3,"difficulty":2,"prompt":"How can you read a possibly missing dictionary key with a fallback?","options":["dict.key","dict.get(key, fallback)","dict[key, fallback]","get.dict(key)"],"answer":1,"explanation":"dict.get accepts a default returned when the key is absent."},
 {"id":"p1","topic":4,"difficulty":1,"prompt":"What is the largest value in [4, 9, 2]?","options":["4","9","2","It depends"],"answer":1,"explanation":"9 is greater than 4 and 2."},
 {"id":"p2","topic":4,"difficulty":2,"prompt":"Which creates squares from 0 through 3?","options":["[x*x for x in range(4)]","[x^2 for x in 4]","square(range(4))","range(4*x)"],"answer":0,"explanation":"The comprehension squares each value produced by range(4)."},
 {"id":"b1","topic":5,"difficulty":1,"prompt":"A SyntaxError usually means…","options":["Code violates Python grammar","A value is wrong","It ran slowly","A file is missing"],"answer":0,"explanation":"Python cannot parse the program structure."},
 {"id":"b2","topic":5,"difficulty":2,"prompt":"Why can dictionary indexing raise KeyError?","options":["Dictionary is empty","Requested key is missing","Values must be strings","print cannot take dicts"],"answer":1,"explanation":"Indexing with an absent key raises KeyError; get() can supply a default."},
]
class ProfileIn(BaseModel):
    name: str = Field(min_length=1, max_length=100); career: str = "AI/ML Engineer"; skill: str = "Python"; level: str = "Beginner"; preferences: dict = {}
class AnswerIn(BaseModel): question_id: str; choice: int = Field(ge=0, le=5)
class MilestoneIn(BaseModel): completed: bool
def owner(x_user_id: Optional[str]) -> str:
    # Local demo only. Production must replace this header with a verified Supabase/JWT subject.
    if not x_user_id or len(x_user_id) > 80: raise HTTPException(401, "Sign in required")
    return x_user_id
def db(): return Session()

@app.get("/api/health")
def health(): return {"status":"ok","mode":"development demo"}
@app.put("/api/profile")
def put_profile(body: ProfileIn, x_user_id: Optional[str] = Header(None)):
    uid=owner(x_user_id)
    if body.career != "AI/ML Engineer" or body.skill != "Python": raise HTTPException(422,"Only the Python to AI/ML pathway is enabled in this MVP")
    with db() as s:
        p=s.get(Profile,uid) or Profile(id=uid); p.name=body.name; p.career=body.career; p.skill=body.skill; p.level=body.level; p.preferences=json.dumps(body.preferences); s.add(p); s.commit()
    return {"id":uid,"name":body.name,"career":body.career,"skill":body.skill,"level":body.level}
@app.post("/api/assessments")
def start_assessment(x_user_id: Optional[str] = Header(None)):
    uid=owner(x_user_id)
    with db() as s:
        if not s.get(Profile,uid): raise HTTPException(409,"Complete onboarding first")
        a=Assessment(owner_id=uid); s.add(a); s.commit(); s.refresh(a); return {"id":a.id,"status":a.status,"question":public_question(QUESTIONS[0])}
def public_question(q): return {k:v for k,v in q.items() if k not in ("answer","explanation")}
@app.get("/api/assessments/{assessment_id}/next")
def next_question(assessment_id: int, x_user_id: Optional[str] = Header(None)):
    uid=owner(x_user_id)
    with db() as s:
        a=s.get(Assessment,assessment_id)
        if not a or a.owner_id != uid: raise HTTPException(404,"Assessment not found")
        if a.status != "in_progress": raise HTTPException(409,"Assessment is complete")
        answers=json.loads(a.answers); used={x["question_id"] for x in answers}; remaining=[q for q in QUESTIONS if q["id"] not in used]
        if len(answers)>=12 or not remaining: return {"complete":True}
        recent=answers[-2:]; topic=min(range(len(TOPICS)),key=lambda t:sum(x["topic"]==t for x in answers))
        difficulty=1
        if len(recent)>=2 and all(x["correct"] for x in recent): difficulty=2
        elif recent and not recent[-1]["correct"]: difficulty=1
        pool=[q for q in remaining if q["topic"]==topic and q["difficulty"]==difficulty] or [q for q in remaining if q["topic"]==topic] or remaining
        return {"complete":False,"question":public_question(random.choice(pool)),"number":len(answers)+1}
@app.post("/api/assessments/{assessment_id}/answers")
def submit_answer(assessment_id: int, body: AnswerIn, x_user_id: Optional[str] = Header(None)):
    uid=owner(x_user_id); q=next((q for q in QUESTIONS if q["id"]==body.question_id),None)
    if not q: raise HTTPException(404,"Question not found")
    with db() as s:
        a=s.get(Assessment,assessment_id)
        if not a or a.owner_id != uid: raise HTTPException(404,"Assessment not found")
        if a.status!="in_progress": raise HTTPException(409,"Assessment is complete")
        answers=json.loads(a.answers)
        if any(x["question_id"]==body.question_id for x in answers): raise HTTPException(409,"Question already answered")
        correct=body.choice==q["answer"]; answers.append({"question_id":q["id"],"topic":q["topic"],"correct":correct,"choice":body.choice}); a.answers=json.dumps(answers); s.commit()
        return {"saved":True,"correct":correct,"explanation":q["explanation"],"progress":len(answers)/12}
@app.post("/api/assessments/{assessment_id}/complete")
def complete_assessment(assessment_id: int, x_user_id: Optional[str] = Header(None)):
    uid=owner(x_user_id)
    with db() as s:
        a=s.get(Assessment,assessment_id)
        if not a or a.owner_id!=uid: raise HTTPException(404,"Assessment not found")
        answers=json.loads(a.answers)
        if len(answers)<6: raise HTTPException(409,"Answer at least six questions before completing")
        a.status="completed"; s.commit(); topics=[]
        for i,name in enumerate(TOPICS):
            rows=[x for x in answers if x["topic"]==i]; topics.append({"topic":name,"answered":len(rows),"accuracy":round(sum(x["correct"] for x in rows)/len(rows)*100) if rows else None})
        return {"id":a.id,"quiz_score":round(sum(x["correct"] for x in answers)/len(answers)*100),"topics":topics,"answers":len(answers),"practical":"not_assessed"}
@app.get("/api/progress")
def progress(x_user_id: Optional[str] = Header(None)):
    uid=owner(x_user_id)
    with db() as s:
        rows=s.scalars(select(Assessment).where(Assessment.owner_id==uid,Assessment.status=="completed").order_by(Assessment.created_at)).all()
        return [{"id":a.id,"created_at":a.created_at,"answers":json.loads(a.answers)} for a in rows]
@app.put("/api/roadmap/{milestone_id}")
def update_milestone(milestone_id: str, body: MilestoneIn, x_user_id: Optional[str] = Header(None)):
    uid=owner(x_user_id)
    with db() as s:
        row=s.get(Milestone,milestone_id)
        if not row or row.owner_id!=uid: raise HTTPException(404,"Milestone not found")
        row.completed=body.completed; s.commit(); return {"id":row.id,"completed":row.completed}
