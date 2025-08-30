from fastapi import APIRouter

router = APIRouter()


@router.post('/postproject')
async def post_project():
    pass