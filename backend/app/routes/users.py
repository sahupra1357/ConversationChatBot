from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional, List
import os

from app.deps import get_db
from app.crud import getUserById, getUserByUsername
from app.model import Users
from app.config import local_settings

router = APIRouter(tags=["users"])

@router.get("/admin-user", response_model=dict, status_code=status.HTTP_200_OK)
def get_admin_user(db: Session = Depends(get_db)):
    """Get the admin user ID for client applications"""
    try:
        # Log the expected admin username we're looking for
        print(f"Looking for admin user with username: {local_settings.FIRST_SUPERUSER}")
        
        if not local_settings.FIRST_SUPERUSER:
            error_msg = "FIRST_SUPERUSER environment variable is not set"
            print(f"Error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
            
        # Get user by username, not by ID
        user = getUserByUsername(session=db, username=local_settings.FIRST_SUPERUSER)
        
        if not user:
            # Fallback to the username if user not found
            print(f"Admin user not found in database, using default: {local_settings.FIRST_SUPERUSER}")
            return {
                "userId": local_settings.FIRST_SUPERUSER, 
                "isDefault": True,
                "message": "Admin user not found in database, using username as fallback"
            }
            
        if not user.id:
            error_msg = f"Admin user found but has no valid ID: {user.username}"
            print(f"Error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg
            )
            
        print(f"Found admin user: {user.username} with ID: {user.id}")
        return {"userId": user.id, "username": user.username, "isDefault": False}
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = f"Error getting admin user: {str(e)}"
        print(f"Exception: {error_msg}")
        # Return a proper error response
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
