from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DB_PATH = "daily_goals.db"

app = FastAPI(title="Daily Goals API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
    ,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            goal_date TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'open',
            note TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS retrospectives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            retro_date TEXT NOT NULL,
            went_well TEXT,
            challenges TEXT,
            next_steps TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects (id)
        );
        """
    )
    conn.commit()
    conn.close()


@app.on_event("startup")
def on_startup() -> None:
    init_db()


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1)
    active: bool = True


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    active: Optional[bool] = None


class ProjectOut(BaseModel):
    id: int
    name: str
    active: bool
    created_at: str


class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1)
    goal_date: Optional[str] = None
    status: str = "open"
    note: Optional[str] = None


class GoalOut(BaseModel):
    id: int
    project_id: int
    title: str
    goal_date: str
    status: str
    note: Optional[str]
    created_at: str


class RetroCreate(BaseModel):
    retro_date: Optional[str] = None
    went_well: Optional[str] = None
    challenges: Optional[str] = None
    next_steps: Optional[str] = None


class RetroOut(BaseModel):
    id: int
    project_id: int
    retro_date: str
    went_well: Optional[str]
    challenges: Optional[str]
    next_steps: Optional[str]
    created_at: str


class DashboardOut(BaseModel):
    today: str
    active_projects: List[ProjectOut]
    todays_goals: List[GoalOut]


@dataclass
class DbRow:
    row: sqlite3.Row

    def to_project(self) -> ProjectOut:
        return ProjectOut(
            id=self.row["id"],
            name=self.row["name"],
            active=bool(self.row["active"]),
            created_at=self.row["created_at"],
        )

    def to_goal(self) -> GoalOut:
        return GoalOut(
            id=self.row["id"],
            project_id=self.row["project_id"],
            title=self.row["title"],
            goal_date=self.row["goal_date"],
            status=self.row["status"],
            note=self.row["note"],
            created_at=self.row["created_at"],
        )

    def to_retro(self) -> RetroOut:
        return RetroOut(
            id=self.row["id"],
            project_id=self.row["project_id"],
            retro_date=self.row["retro_date"],
            went_well=self.row["went_well"],
            challenges=self.row["challenges"],
            next_steps=self.row["next_steps"],
            created_at=self.row["created_at"],
        )


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def today_iso() -> str:
    return date.today().isoformat()


@app.get("/api/projects", response_model=List[ProjectOut])
def list_projects(active: Optional[bool] = None) -> List[ProjectOut]:
    conn = get_conn()
    cur = conn.cursor()
    if active is None:
        cur.execute("SELECT * FROM projects ORDER BY created_at DESC")
    else:
        cur.execute(
            "SELECT * FROM projects WHERE active = ? ORDER BY created_at DESC",
            (1 if active else 0,),
        )
    rows = cur.fetchall()
    conn.close()
    return [DbRow(row).to_project() for row in rows]


@app.post("/api/projects", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate) -> ProjectOut:
    conn = get_conn()
    cur = conn.cursor()
    created_at = now_iso()
    cur.execute(
        "INSERT INTO projects (name, active, created_at) VALUES (?, ?, ?)",
        (payload.name, 1 if payload.active else 0, created_at),
    )
    project_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    conn.close()
    return DbRow(row).to_project()


@app.get("/api/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int) -> ProjectOut:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return DbRow(row).to_project()


@app.patch("/api/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate) -> ProjectOut:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")

    name = payload.name if payload.name is not None else row["name"]
    active = payload.active if payload.active is not None else bool(row["active"])
    cur.execute(
        "UPDATE projects SET name = ?, active = ? WHERE id = ?",
        (name, 1 if active else 0, project_id),
    )
    conn.commit()
    cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    updated = cur.fetchone()
    conn.close()
    return DbRow(updated).to_project()


@app.get("/api/projects/{project_id}/goals", response_model=List[GoalOut])
def list_goals(project_id: int) -> List[GoalOut]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")
    cur.execute(
        "SELECT * FROM goals WHERE project_id = ? ORDER BY goal_date DESC, created_at DESC",
        (project_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [DbRow(row).to_goal() for row in rows]


@app.post("/api/projects/{project_id}/goals", response_model=GoalOut, status_code=201)
def create_goal(project_id: int, payload: GoalCreate) -> GoalOut:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")

    goal_date = payload.goal_date or today_iso()
    created_at = now_iso()
    cur.execute(
        """
        INSERT INTO goals (project_id, title, goal_date, status, note, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (project_id, payload.title, goal_date, payload.status, payload.note, created_at),
    )
    goal_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM goals WHERE id = ?", (goal_id,))
    row = cur.fetchone()
    conn.close()
    return DbRow(row).to_goal()


@app.get("/api/projects/{project_id}/retros", response_model=List[RetroOut])
def list_retros(project_id: int) -> List[RetroOut]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")
    cur.execute(
        "SELECT * FROM retrospectives WHERE project_id = ? ORDER BY retro_date DESC, created_at DESC",
        (project_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [DbRow(row).to_retro() for row in rows]


@app.post("/api/projects/{project_id}/retros", response_model=RetroOut, status_code=201)
def create_retro(project_id: int, payload: RetroCreate) -> RetroOut:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
    if cur.fetchone() is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Project not found")

    retro_date = payload.retro_date or today_iso()
    created_at = now_iso()
    cur.execute(
        """
        INSERT INTO retrospectives (project_id, retro_date, went_well, challenges, next_steps, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            project_id,
            retro_date,
            payload.went_well,
            payload.challenges,
            payload.next_steps,
            created_at,
        ),
    )
    retro_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM retrospectives WHERE id = ?", (retro_id,))
    row = cur.fetchone()
    conn.close()
    return DbRow(row).to_retro()


@app.get("/api/dashboard", response_model=DashboardOut)
def get_dashboard() -> DashboardOut:
    conn = get_conn()
    cur = conn.cursor()
    today = today_iso()
    cur.execute("SELECT * FROM projects WHERE active = 1 ORDER BY created_at DESC")
    projects = [DbRow(row).to_project() for row in cur.fetchall()]

    cur.execute(
        """
        SELECT * FROM goals
        WHERE goal_date = ?
        ORDER BY created_at DESC
        """,
        (today,),
    )
    goals = [DbRow(row).to_goal() for row in cur.fetchall()]
    conn.close()
    return DashboardOut(today=today, active_projects=projects, todays_goals=goals)
