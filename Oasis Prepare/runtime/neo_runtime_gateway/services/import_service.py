import os
from uuid import UUID
from typing import List
from schemas.import_request import ImportRequest, ImportResult, ResourceType
from services.event_service import EventService

class ImportService:
    def __init__(self, event_service: EventService):
        self.event_service = event_service

    async def import_assets(self, request: ImportRequest) -> ImportResult:
        success_count = 0
        failed_count = 0
        imported_paths = []
        failed_paths = []
        errors = []

        target_dir = request.target_directory
        if not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)

        for file_path in request.files:
            try:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    dest_path = os.path.join(target_dir, file_name)
                    
                    import shutil
                    shutil.copy(file_path, dest_path)
                    
                    imported_paths.append(dest_path)
                    success_count += 1
                else:
                    failed_paths.append(file_path)
                    errors.append(f"File not found: {file_path}")
                    failed_count += 1
            except Exception as e:
                failed_paths.append(file_path)
                errors.append(f"Failed to import {file_path}: {str(e)}")
                failed_count += 1

        await self.event_service.publish_event(
            session_id=request.session_id,
            event_type="artifact.ready",
            payload={
                "imported_paths": imported_paths,
                "failed_paths": failed_paths
            }
        )

        return ImportResult(
            success=failed_count == 0,
            imported_paths=imported_paths,
            failed_paths=failed_paths,
            errors=errors,
            message=f"Imported {success_count} files, {failed_count} failed"
        )