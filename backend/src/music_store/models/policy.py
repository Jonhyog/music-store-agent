from pydantic import BaseModel


class PolicyChunkModel(BaseModel):
    """One subsection of the Policy Manual (or a section's own intro) with its section number."""

    section: str
    title: str
    parent_title: str | None
    text: str

    @property
    def heading(self) -> str:
        return f"{self.section} {self.title}"

    @property
    def content(self) -> str:
        """The text that is embedded: parent section title, then the subsection."""
        head = [self.parent_title, self.heading] if self.parent_title else [self.heading]
        return "\n".join([*head, self.text])
