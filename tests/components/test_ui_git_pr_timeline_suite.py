import pytest
import cairo
from vibmo.product.ai.ui_git_pr_timeline_suite import (
    GitPullRequestCard,
    CommitShaBadge,
    CiCdCheckStatusPill,
    MergeSquashButton,
    GitPrTimeline,
    MergeStatusPill,
)

def test_git_pr_card_open():
    card = GitPullRequestCard(pr_number=88, title="Add 100+ components", state="open")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 200)
    ctx = cairo.Context(surface)
    card.draw(ctx, time=0.0)
    assert card.pr_number == 88

def test_git_pr_card_merged():
    card = GitPullRequestCard(pr_number=88, title="Add 100+ components", state="merged")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 600, 200)
    ctx = cairo.Context(surface)
    card.draw(ctx, time=0.0)
    assert card.state == "merged"

def test_commit_sha_badge():
    badge = CommitShaBadge(sha="1234abc")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
    ctx = cairo.Context(surface)
    badge.draw(ctx, time=0.0)
    assert badge.sha == "1234abc"

def test_cicd_check_passed():
    pill = CiCdCheckStatusPill(status="passed")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
    ctx = cairo.Context(surface)
    pill.draw(ctx, time=0.0)
    assert pill.status == "passed"

def test_cicd_check_pending():
    pill = CiCdCheckStatusPill(status="pending")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
    ctx = cairo.Context(surface)
    pill.draw(ctx, time=0.0)
    assert pill.status == "pending"

def test_merge_squash_button():
    btn = MergeSquashButton(label="Squash and Merge")
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 50)
    ctx = cairo.Context(surface)
    btn.draw(ctx, time=0.0)
    assert btn.label == "Squash and Merge"
