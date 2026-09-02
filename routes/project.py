from fastapi import APIRouter, HTTPException, Depends, status
from model.project import projectModel as Project, ProjectOut
from database.config import project_collection
from routes.user import get_current_user
from core.object_id import parse_object_id, serialize_doc
from core.slugify import slugify, unique_slug
from typing import List, Optional

router = APIRouter()


def _generate_unique_slug(title: str, exclude_id: Optional[str] = None) -> str:
    base = slugify(title)

    def slug_taken(candidate: str) -> bool:
        query = {"slug": candidate}
        if exclude_id:
            query["_id"] = {"$ne": parse_object_id(exclude_id)}
        return project_collection.find_one(query) is not None

    return unique_slug(base, slug_taken)


@router.post(
    "/projects/",
    response_model=ProjectOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_user)],
)
def create_project(project: Project):
    slug = _generate_unique_slug(project.title)
    doc = {**project.model_dump(), "slug": slug}
    result = project_collection.insert_one(doc)
    return ProjectOut(id=str(result.inserted_id), **doc)

@router.get("/projects/", response_model=List[ProjectOut])
def get_projects():
    return [serialize_doc(proj) for proj in project_collection.find({})]

@router.get("/projects/slug/{slug}", response_model=ProjectOut, summary="Get one project by its public URL slug")
def get_project_by_slug(slug: str):
    doc = project_collection.find_one({"slug": slug})
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found.")
    return serialize_doc(doc)

@router.put("/projects/{project_id}", response_model=ProjectOut, dependencies=[Depends(get_current_user)])
def update_project(project_id: str, project: Project):
    oid = parse_object_id(project_id)
    existing = project_collection.find_one({"_id": oid})
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project entry not found.")

    # The slug is stable: it does not change when the title changes, so
    # links and bookmarks to /projects/{slug} keep working after an edit.
    slug = existing.get("slug") or _generate_unique_slug(project.title, exclude_id=project_id)

    doc = {**project.model_dump(), "slug": slug}
    project_collection.update_one({"_id": oid}, {"$set": doc})
    return ProjectOut(id=project_id, **doc)

@router.delete("/projects/{project_id}", dependencies=[Depends(get_current_user)])
def delete_project(project_id: str):
    oid = parse_object_id(project_id)
    result = project_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project entry not found.")
    return {"detail": "Project entry deleted successfully."}


def migrate_project_slugs() -> None:
    """Backfill a slug for any project saved before the slug field existed.

    Must run before the unique index on `slug` is created, since Mongo
    treats a missing field as null and a unique index would otherwise
    reject the second legacy project it finds.
    """
    for doc in project_collection.find({"slug": {"$exists": False}}):
        slug = _generate_unique_slug(doc.get("title") or "project")
        project_collection.update_one({"_id": doc["_id"]}, {"$set": {"slug": slug}})
