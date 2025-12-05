from abc import ABC, abstractmethod
from mcp.types import Resource, TextResourceContents


class BaseResource(ABC):

    name: str
    description: str
    mime_type: str = "text/plain"

    @abstractmethod
    def get_uri(self) -> str:
        pass

    @abstractmethod
    async def read(self) -> str:
        pass

    def to_mcp_resource(self) -> Resource:
        return Resource(
            uri=self.get_uri(),
            name=self.name,
            description=self.description,
            mime_type=self.mime_type
        )
    
    async def to_resource_contents(self) -> TextResourceContents:
        content = await self.read()
        return TextResourceContents(
            uri=self.get_uri(),
            mime_type=self.mime_type,
            text=content
        )
    
class DynamicResource(BaseResource):
    uri_template: str

    def __init__(self, **params):
        self.params = params

    def get_uri(self) -> str:
        uri = self.uri_template
        for key, value in self.params.items():
            uri = uri.replace(f"{{{key}}}", str(value))
        return uri
