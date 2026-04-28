from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load_volunteers():
    with open("volunteers.json", "r") as f:
        return json.load(f)["volunteers"]

class TaskRequest(BaseModel):
    task_description: str

@app.get("/")
def root():
    return {"status": "running", "project": "Volunteer Coordinator AI"}

@app.get("/volunteers")
def get_volunteers():
    return {"volunteers": load_volunteers()}

@app.post("/match")
def match_volunteers(request: TaskRequest):
    volunteers = load_volunteers()
    task = request.task_description.lower()
    scored = []
    for v in volunteers:
        score = 0
        reasons = []
        for skill in v["skills"]:
            if skill.lower() in task:
                score += 3
                reasons.append(f"has '{skill}' skill matching the task")
        if v["location"].lower() in task:
            score += 2
            reasons.append(f"located in {v['location']}")
        if v["availability"].lower() in task:
            score += 2
            reasons.append(f"available on {v['availability']}")
        score += v["experience_years"] * 0.5
        score += v["past_tasks"] * 0.1
        if not reasons:
            reasons.append(f"has {v['experience_years']} years experience and {v['past_tasks']} past tasks")
        scored.append({"volunteer": v, "score": score, "reasons": reasons})
    scored.sort(key=lambda x: x["score"], reverse=True)
    top3 = scored[:3]
    matches = []
    for i, item in enumerate(top3):
        v = item["volunteer"]
        matches.append({
            "rank": i+1,
            "name": v["name"],
            "reason": f"{v['name']} is a great match because they " + ", ".join(item["reasons"]) + f". They have {v['experience_years']} years of experience and completed {v['past_tasks']} past tasks."
        })
    return {"matches": matches}