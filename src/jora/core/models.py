"""Pydantic data models for Jira entities."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ..utils.time_utils import format_time_estimate

# Pre-compiled patterns for Jira ISO 8601 datetime normalization.
# Jira returns e.g. "2026-04-07T10:30:00.000+0900"; fromisoformat requires
# "2026-04-07T10:30:00+09:00" (no ms, colon in tz offset).
_RE_MILLISECONDS = re.compile(r"\.\d+")
_RE_TZ_OFFSET = re.compile(r"([+-]\d{2})(\d{2})$")


def _parse_jira_datetime(val: Any) -> Optional[datetime]:
    """Parse a Jira ISO 8601 datetime string to a timezone-aware datetime."""
    if not val:
        return None
    try:
        s = _RE_MILLISECONDS.sub("", str(val))
        s = _RE_TZ_OFFSET.sub(r"\1:\2", s)
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _extract_jira_user(u: Any) -> Optional["JiraUser"]:
    """Convert a raw Jira user object to a JiraUser model."""
    if not u:
        return None
    return JiraUser(
        account_id=getattr(u, "accountId", "") or getattr(u, "name", ""),
        display_name=getattr(u, "displayName", "Unknown"),
        email_address=getattr(u, "emailAddress", None),
    )


class JiraUser(BaseModel):
    account_id: str = ""
    display_name: str = "Unknown"
    email_address: Optional[str] = None


class TimeTracking(BaseModel):
    original_estimate: Optional[str] = None
    original_estimate_seconds: Optional[int] = None
    remaining_estimate: Optional[str] = None
    remaining_estimate_seconds: Optional[int] = None
    time_spent: Optional[str] = None
    time_spent_seconds: Optional[int] = None


class Issue(BaseModel):
    key: str
    summary: str
    status: str
    issue_type: str = "Unknown"
    priority: Optional[str] = None
    assignee: Optional[JiraUser] = None
    reporter: Optional[JiraUser] = None
    fix_versions: List[str] = []
    labels: List[str] = []
    description: Optional[str] = None
    time_tracking: TimeTracking = TimeTracking()
    created: Optional[datetime] = None
    updated: Optional[datetime] = None
    url: Optional[str] = None

    @classmethod
    def from_jira_issue(cls, raw: Any, server_url: str) -> "Issue":
        """Factory that converts a jira.Issue object to our Pydantic model."""
        f = raw.fields

        tt = TimeTracking(
            original_estimate=format_time_estimate(getattr(f, "timeoriginalestimate", None)),
            original_estimate_seconds=getattr(f, "timeoriginalestimate", None),
            remaining_estimate=format_time_estimate(getattr(f, "timeestimate", None)),
            remaining_estimate_seconds=getattr(f, "timeestimate", None),
            time_spent=format_time_estimate(getattr(f, "timespent", None)),
            time_spent_seconds=getattr(f, "timespent", None),
        )

        return cls(
            key=raw.key,
            summary=getattr(f, "summary", ""),
            status=getattr(f.status, "name", "Unknown") if getattr(f, "status", None) else "Unknown",
            issue_type=getattr(f.issuetype, "name", "Unknown") if getattr(f, "issuetype", None) else "Unknown",
            priority=getattr(f.priority, "name", None) if getattr(f, "priority", None) else None,
            assignee=_extract_jira_user(getattr(f, "assignee", None)),
            reporter=_extract_jira_user(getattr(f, "reporter", None)),
            fix_versions=[v.name for v in (getattr(f, "fixVersions", None) or [])],
            labels=list(getattr(f, "labels", None) or []),
            description=getattr(f, "description", None),
            time_tracking=tt,
            created=_parse_jira_datetime(getattr(f, "created", None)),
            updated=_parse_jira_datetime(getattr(f, "updated", None)),
            url=f"{server_url.rstrip('/')}/browse/{raw.key}",
        )


class Worklog(BaseModel):
    id: str
    author: JiraUser
    time_spent: str
    time_spent_seconds: int
    started: datetime
    comment: Optional[str] = None
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    @classmethod
    def from_jira_worklog(cls, raw: Any) -> "Worklog":
        return cls(
            id=str(raw.id),
            author=_extract_jira_user(getattr(raw, "author", None)) or JiraUser(),
            time_spent=getattr(raw, "timeSpent", ""),
            time_spent_seconds=getattr(raw, "timeSpentSeconds", 0),
            started=_parse_jira_datetime(getattr(raw, "started", None)) or datetime.utcnow(),
            comment=getattr(raw, "comment", None),
            created=_parse_jira_datetime(getattr(raw, "created", None)),
            updated=_parse_jira_datetime(getattr(raw, "updated", None)),
        )


class Comment(BaseModel):
    id: str
    author: JiraUser
    body: str
    created: Optional[datetime] = None
    updated: Optional[datetime] = None

    @classmethod
    def from_jira_comment(cls, raw: Any) -> "Comment":
        return cls(
            id=str(raw.id),
            author=_extract_jira_user(getattr(raw, "author", None)) or JiraUser(),
            body=getattr(raw, "body", ""),
            created=_parse_jira_datetime(getattr(raw, "created", None)),
            updated=_parse_jira_datetime(getattr(raw, "updated", None)),
        )


class IssueLinkType(BaseModel):
    id: str
    name: str
    inward: str
    outward: str

    @classmethod
    def from_jira_link_type(cls, raw: Any) -> "IssueLinkType":
        return cls(
            id=str(raw.id),
            name=getattr(raw, "name", ""),
            inward=getattr(raw, "inward", ""),
            outward=getattr(raw, "outward", ""),
        )


class IssueLink(BaseModel):
    id: str
    link_type: str
    direction_text: str
    linked_issue_key: str
    linked_issue_summary: Optional[str] = None
    linked_issue_status: Optional[str] = None

    @classmethod
    def from_jira_link(cls, raw: Any) -> "IssueLink":
        """Convert a raw jira issuelink object to IssueLink.

        Jira attaches either inwardIssue or outwardIssue depending on perspective.
        We normalise to a single linked_issue_key + direction_text pair.
        """
        link_type = getattr(raw, "type", None)
        type_name = getattr(link_type, "name", "")
        inward_text = getattr(link_type, "inward", "")
        outward_text = getattr(link_type, "outward", "")

        outward_issue = getattr(raw, "outwardIssue", None)
        inward_issue = getattr(raw, "inwardIssue", None)

        if outward_issue is not None:
            linked_key = getattr(outward_issue, "key", "")
            direction_text = outward_text
            summary = getattr(getattr(outward_issue, "fields", None), "summary", None)
            status_obj = getattr(getattr(outward_issue, "fields", None), "status", None)
            status = getattr(status_obj, "name", None) if status_obj else None
        else:
            linked_key = getattr(inward_issue, "key", "") if inward_issue else ""
            direction_text = inward_text
            summary = getattr(getattr(inward_issue, "fields", None), "summary", None) if inward_issue else None
            status_obj = getattr(getattr(inward_issue, "fields", None), "status", None) if inward_issue else None
            status = getattr(status_obj, "name", None) if status_obj else None

        return cls(
            id=str(raw.id),
            link_type=type_name,
            direction_text=direction_text,
            linked_issue_key=linked_key,
            linked_issue_summary=summary,
            linked_issue_status=status,
        )


class OperationResult(BaseModel):
    success: bool
    issue_key: Optional[str] = None
    message: str
    data: Optional[Dict[str, Any]] = None


class ErrorResult(BaseModel):
    error: str
    code: str = "ERROR"
    details: Optional[str] = None
