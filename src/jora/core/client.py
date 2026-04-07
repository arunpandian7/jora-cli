"""JoraClient — all Jira API interactions, no I/O, typed exceptions."""

from __future__ import annotations

from typing import Any, List, Optional

from jira import JIRA

from .config import ProfileConfig, resolve_token
from .models import Comment, Issue, OperationResult, Worklog
from ..utils.time_utils import parse_datetime, parse_time_input, seconds_to_jira_format


# ---------------------------------------------------------------------------
# Typed exceptions
# ---------------------------------------------------------------------------

class JoraError(Exception):
    def __init__(self, message: str, code: str = "JORA_ERROR"):
        self.message = message
        self.code = code
        super().__init__(message)


class AuthError(JoraError):
    def __init__(self, message: str):
        super().__init__(message, "AUTH_FAILED")


class NotFoundError(JoraError):
    def __init__(self, message: str):
        super().__init__(message, "NOT_FOUND")


class PermissionError(JoraError):
    def __init__(self, message: str):
        super().__init__(message, "PERMISSION_DENIED")


class JiraAPIError(JoraError):
    def __init__(self, message: str):
        super().__init__(message, "API_ERROR")


class InvalidInputError(JoraError):
    def __init__(self, message: str):
        super().__init__(message, "INVALID_INPUT")


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class JoraClient:
    def __init__(self, profile: ProfileConfig, profile_name: str = "default"):
        token = resolve_token(profile, profile_name)
        self._server = profile.server.rstrip("/")
        self._profile = profile

        try:
            self._jira = JIRA(
                server=self._server,
                token_auth=token,
                options={
                    "verify": profile.verify_ssl,
                    "server": self._server,
                },
            )
            self._current_user = self._jira.current_user()
        except Exception as e:
            msg = str(e)
            if "401" in msg or "Unauthorized" in msg.lower():
                raise AuthError(f"Authentication failed: {msg}")
            if "403" in msg or "Forbidden" in msg.lower():
                raise PermissionError(f"Permission denied: {msg}")
            raise AuthError(f"Could not connect to {self._server}: {msg}")

    @property
    def current_user(self) -> str:
        return self._current_user

    @staticmethod
    def _assignee_clause(assignee: str) -> str:
        """Build a JQL assignee filter clause."""
        if assignee.lower() == "me":
            return "assignee = currentUser()"
        return f'assignee = "{assignee}"'

    # ------------------------------------------------------------------
    # Issue operations
    # ------------------------------------------------------------------

    def get_issue(self, key: str) -> Issue:
        """Fetch a single issue by key."""
        try:
            raw = self._jira.issue(key)
            return Issue.from_jira_issue(raw, self._server)
        except JoraError:
            raise
        except Exception as e:
            msg = str(e)
            if "404" in msg or "does not exist" in msg.lower():
                raise NotFoundError(f"Issue '{key}' not found.")
            if "403" in msg or "permission" in msg.lower():
                raise PermissionError(f"No permission to read '{key}'.")
            raise JiraAPIError(f"Failed to get issue '{key}': {msg}")

    def search_issues(
        self,
        jql: str,
        max_results: int = 50,
    ) -> List[Issue]:
        """Execute a raw JQL search and return Issue models."""
        try:
            raw_issues = self._jira.search_issues(jql, maxResults=max_results)
            return [Issue.from_jira_issue(r, self._server) for r in raw_issues]
        except JoraError:
            raise
        except Exception as e:
            msg = str(e)
            if "400" in msg:
                raise InvalidInputError(f"Invalid JQL query: {msg}")
            raise JiraAPIError(f"Search failed: {msg}")

    def build_filter_jql(
        self,
        project: Optional[str] = None,
        fix_version: Optional[str] = None,
        assignee: Optional[str] = None,
        status: Optional[str] = None,
        extra_jql: Optional[str] = None,
    ) -> str:
        """Compose a JQL query from common filter parameters."""
        parts = []
        if project:
            parts.append(f'project = "{project}"')
        if fix_version:
            parts.append(f'fixVersion = "{fix_version}"')
        if assignee:
            parts.append(self._assignee_clause(assignee))
        if status:
            parts.append(f'status = "{status}"')
        if extra_jql:
            parts.append(f"({extra_jql})")
        return " AND ".join(parts) if parts else "project is not EMPTY"

    def create_issue(
        self,
        project: str,
        summary: str,
        description: Optional[str] = None,
        issue_type: str = "Task",
        assignee: Optional[str] = None,
        fix_version: Optional[str] = None,
        original_estimate: Optional[str] = None,
    ) -> OperationResult:
        """Create a new issue."""
        fields: dict = {
            "project": {"key": project},
            "summary": summary,
            "issuetype": {"name": issue_type},
        }
        if description:
            fields["description"] = description
        if assignee:
            if assignee.lower() == "me":
                fields["assignee"] = {"name": self._jira.current_user()}
            else:
                fields["assignee"] = {"name": assignee}
        if fix_version:
            fields["fixVersions"] = [{"name": fix_version}]
        if original_estimate:
            try:
                secs = parse_time_input(original_estimate)
                if secs:
                    fields["timetracking"] = {"originalEstimate": seconds_to_jira_format(secs)}
            except ValueError as e:
                raise InvalidInputError(str(e))

        try:
            new_issue = self._jira.create_issue(fields=fields)
            return OperationResult(
                success=True,
                issue_key=new_issue.key,
                message=f"Created issue {new_issue.key}",
                data={"url": f"{self._server}/browse/{new_issue.key}"},
            )
        except JoraError:
            raise
        except Exception as e:
            raise JiraAPIError(f"Failed to create issue: {e}")

    def update_issue(
        self,
        key: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        assignee: Optional[str] = None,
        fix_version: Optional[str] = None,
        original_estimate: Optional[str] = None,
    ) -> OperationResult:
        """Update fields on an existing issue."""
        try:
            raw = self._jira.issue(key)
        except Exception as e:
            msg = str(e)
            if "404" in msg:
                raise NotFoundError(f"Issue '{key}' not found.")
            raise JiraAPIError(f"Failed to fetch '{key}': {msg}")

        fields: dict = {}
        if summary is not None:
            fields["summary"] = summary
        if description is not None:
            fields["description"] = description
        if assignee is not None:
            if assignee.lower() == "me":
                fields["assignee"] = {"name": self._jira.current_user()}
            else:
                fields["assignee"] = {"name": assignee}
        if fix_version is not None:
            fields["fixVersions"] = [{"name": fix_version}]
        if original_estimate is not None:
            # Pass already-fetched raw issue to avoid a second network call
            result = self._apply_estimate(raw, original_estimate)
            if not result.success:
                return result

        if fields:
            try:
                raw.update(fields=fields)
            except Exception as e:
                raise JiraAPIError(f"Failed to update '{key}': {e}")

        return OperationResult(success=True, issue_key=key, message=f"Updated {key}")

    def add_comment(self, key: str, body: str) -> OperationResult:
        """Add a comment to an issue."""
        try:
            comment = self._jira.add_comment(key, body)
            return OperationResult(
                success=True,
                issue_key=key,
                message=f"Added comment {comment.id} to {key}",
                data={"comment_id": str(comment.id)},
            )
        except Exception as e:
            raise JiraAPIError(f"Failed to add comment to '{key}': {e}")

    def list_comments(self, key: str) -> List[Comment]:
        """Return all comments for an issue."""
        try:
            raw_comments = self._jira.comments(key)
            return [Comment.from_jira_comment(c) for c in raw_comments]
        except Exception as e:
            raise JiraAPIError(f"Failed to list comments for '{key}': {e}")

    # ------------------------------------------------------------------
    # Time tracking
    # ------------------------------------------------------------------

    def _apply_estimate(self, raw: Any, estimate: str) -> OperationResult:
        """Apply an estimate to an already-fetched raw Jira issue object.

        Tries 'timetracking' field first (Jira Server), falls back to
        'timeoriginalestimate' (some Jira configurations). Both require
        checking editmeta because availability depends on issue type and screen.
        """
        try:
            secs = parse_time_input(estimate)
        except ValueError as e:
            raise InvalidInputError(str(e))

        if secs is None:
            raise InvalidInputError(f"'{estimate}' is not a valid time value.")

        jira_fmt = seconds_to_jira_format(secs)
        key = raw.key

        edit_meta = self._jira.editmeta(key)
        available = set(edit_meta.get("fields", {}).keys())

        if "timetracking" in available:
            raw.update(fields={"timetracking": {"originalEstimate": jira_fmt}})
            return OperationResult(success=True, issue_key=key, message=f"Set original estimate to {jira_fmt} on {key}")
        elif "timeoriginalestimate" in available:
            raw.update(fields={"timeoriginalestimate": secs})
            return OperationResult(success=True, issue_key=key, message=f"Set original estimate to {jira_fmt} on {key}")
        else:
            return OperationResult(
                success=False,
                issue_key=key,
                message=f"Original estimate field is not editable on {key}. "
                        "This may be due to insufficient permissions or field configuration.",
            )

    def set_original_estimate(self, key: str, estimate: str) -> OperationResult:
        """Set the original estimate on an issue."""
        try:
            raw = self._jira.issue(key)
            return self._apply_estimate(raw, estimate)
        except JoraError:
            raise
        except Exception as e:
            raise JiraAPIError(f"Failed to set estimate on '{key}': {e}")

    def add_worklog(
        self,
        key: str,
        time_spent: str,
        comment: Optional[str] = None,
        started: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> OperationResult:
        """Log work on an issue.

        Args:
            key: Issue key.
            time_spent: Time string like '2h 30m'.
            comment: Optional work description.
            started: Optional ISO date/datetime string (YYYY-MM-DD or YYYY-MM-DDTHH:MM).
            timezone: Timezone name; defaults to profile timezone.
        """
        try:
            parse_time_input(time_spent)  # validate
        except ValueError as e:
            raise InvalidInputError(str(e))

        tz = timezone or self._profile.timezone or "UTC"

        date_part: Optional[str] = None
        time_part: Optional[str] = None

        if started:
            if "T" in started:
                parts = started.split("T", 1)
                date_part = parts[0]
                time_part = parts[1][:5] if len(parts) > 1 else None
            else:
                date_part = started

        started_dt = parse_datetime(date_part, time_part, tz)

        try:
            self._jira.add_worklog(
                issue=key,
                timeSpent=time_spent,
                comment=comment or None,
                started=started_dt,
            )
            return OperationResult(
                success=True,
                issue_key=key,
                message=f"Logged {time_spent} on {key}",
            )
        except Exception as e:
            raise JiraAPIError(f"Failed to log work on '{key}': {e}")

    def list_worklogs(self, key: str) -> List[Worklog]:
        """Return all worklogs for an issue."""
        try:
            raw_worklogs = self._jira.worklogs(key)
            return [Worklog.from_jira_worklog(w) for w in raw_worklogs]
        except Exception as e:
            raise JiraAPIError(f"Failed to list worklogs for '{key}': {e}")

    # ------------------------------------------------------------------
    # Batch operations
    # ------------------------------------------------------------------

    def find_incomplete_tickets(
        self,
        project: Optional[str] = None,
        fix_version: Optional[str] = None,
        assignee: Optional[str] = None,
        max_results: int = 50,
    ) -> List[Issue]:
        """Find tickets missing original estimates or with remaining time."""
        parts = []
        if project:
            parts.append(f'project = "{project}"')
        if fix_version:
            parts.append(f'fixVersion = "{fix_version}"')
        if assignee:
            parts.append(self._assignee_clause(assignee))
        parts.append("(originalEstimate is EMPTY OR remainingEstimate > 0)")

        jql = " AND ".join(parts)

        try:
            raw_issues = self._jira.search_issues(jql, maxResults=max_results)
        except Exception as e:
            raise JiraAPIError(f"Batch search failed: {e}")

        results = []
        for raw in raw_issues:
            f = raw.fields
            needs_estimate = not getattr(f, "timeoriginalestimate", None)
            remaining = getattr(f, "timeestimate", None)
            if needs_estimate or (remaining and remaining > 0):
                results.append(Issue.from_jira_issue(raw, self._server))

        return results
