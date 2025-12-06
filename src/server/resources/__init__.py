from pathlib import Path
from .base import BaseResource, DynamicResource
from .file_resources import FileResources, FileResourceProvider
from .project_resources import (
    ProjectStructureResource,
    ProjectSummaryResource,
    ProjectFilesListResource,
    DirectoryContentsResource,
)
from .config_resources import (
    ConfigFileResource,
    ConfigResourceProvider,
    EnvironmentResource,
)


class ResourceManager:
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.file_provider = FileResourceProvider(project_root)
        self.config_provider = ConfigResourceProvider(project_root)
    
    def list_all(self) -> list[BaseResource]:
        resources = []
        
        resources.append(ProjectStructureResource(self.project_root))
        resources.append(ProjectSummaryResource(self.project_root))
        resources.append(ProjectFilesListResource(self.project_root))
        resources.append(DirectoryContentsResource(self.project_root))
        resources.append(EnvironmentResource(self.project_root))
        
        resources.extend(self.config_provider.list_available())
        resources.extend(self.file_provider.list_all())
        
        return resources
    
    async def read(self, uri: str) -> str:
        if uri.startswith("file://"):
            resource = self.file_provider.get_resource(uri)
            return await resource.read()
        
        if uri.startswith("config://"):
            if uri == "config://env":
                resource = EnvironmentResource(self.project_root)
            else:
                resource = self.config_provider.get(uri)
            return await resource.read()
        
        if uri == "project://structure":
            resource = ProjectStructureResource(self.project_root)
            return await resource.read()
        
        if uri == "project://summary":
            resource = ProjectSummaryResource(self.project_root)
            return await resource.read()
        
        if uri == "project://files":
            resource = ProjectFilesListResource(self.project_root)
            return await resource.read()
        
        if uri.startswith("project://dir"):
            directory = uri.replace("project://dir/", "").replace("project://dir", "")
            resource = DirectoryContentsResource(self.project_root, directory)
            return await resource.read()
        
        raise ValueError(f"Unknown resource URI: {uri}")