import pytest
from vibmo.product.ai.ui_git_pr_timeline_suite import (
    GitPullRequestCard,
    CommitShaBadge,
    CiCdCheckStatusPill,
    MergeSquashButton
)
from vibmo.core.color import colors

class MockContext:
    def save(self): pass
    def restore(self): pass
    def translate(self, x, y): pass
    def scale(self, x, y): pass
    def rotate(self, angle): pass
    def set_source_rgba(self, r, g, b, a): pass
    def set_line_width(self, width): pass
    def fill(self): pass
    def stroke(self): pass
    def new_path(self): pass
    def new_sub_path(self): pass
    def rectangle(self, x, y, w, h): pass
    def clip(self): pass
    def arc(self, xc, yc, radius, angle1, angle2): pass
    def close_path(self): pass
    def fill_preserve(self): pass

def test_git_pr_card_open():
    card = GitPullRequestCard(title="Test PR", status="Open")
    assert card.status_text.text.get() == "Open"
    # Status color for open is green
    status_icon_color = card.status_icon.color.get()
    assert status_icon_color.r == colors.GREEN.r
    assert status_icon_color.g == colors.GREEN.g
    assert status_icon_color.b == colors.GREEN.b

    ctx = MockContext()
    card.draw(ctx, 0.0)

def test_git_pr_card_merged():
    card = GitPullRequestCard(title="Test PR", status="Merged")
    assert card.status_text.text.get() == "Merged"
    # Status color for merged is purple
    status_icon_color = card.status_icon.color.get()
    assert status_icon_color.r == colors.PURPLE.r
    assert status_icon_color.g == colors.PURPLE.g
    assert status_icon_color.b == colors.PURPLE.b

    ctx = MockContext()
    card.draw(ctx, 0.0)

def test_commit_sha_badge():
    badge = CommitShaBadge(sha="1234abc", message="Fix bug")
    assert badge.sha_text.text.get() == "1234abc"
    assert badge.message_text.text.get() == "Fix bug"

    ctx = MockContext()
    badge.draw(ctx, 0.0)

def test_cicd_check_passed():
    pill = CiCdCheckStatusPill(status="passed")
    assert pill.status_text.text.get() == "All checks passed"
    icon_color = pill.icon.color.get()
    assert icon_color.r == colors.GREEN.r
    assert icon_color.g == colors.GREEN.g
    assert icon_color.b == colors.GREEN.b

    ctx = MockContext()
    pill.draw(ctx, 0.0)

def test_cicd_check_pending():
    pill = CiCdCheckStatusPill(status="pending", text="Running checks")
    assert pill.status_text.text.get() == "Running checks"
    icon_color = pill.icon.color.get()
    assert icon_color.r == colors.AMBER.r
    assert icon_color.g == colors.AMBER.g
    assert icon_color.b == colors.AMBER.b

    ctx = MockContext()
    pill.draw(ctx, 0.0)

def test_merge_squash_button():
    btn = MergeSquashButton(text="Squash and Merge")
    assert btn.btn_text.text.get() == "Squash and Merge"
    fill_color = btn.fill.get()
    assert fill_color.r == colors.GREEN.r
    assert fill_color.g == colors.GREEN.g
    assert fill_color.b == colors.GREEN.b

    ctx = MockContext()
    btn.draw(ctx, 0.0)
