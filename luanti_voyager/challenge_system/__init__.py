"""
Community Challenge System for Luanti Voyager

This module provides a framework for creating and managing community challenges,
including submission handling, scoring, and leaderboard management.
"""

from .challenge import ChallengeSystem, Challenge, ChallengeType, ChallengeStatus
from .submission import Submission, SubmissionStatus, EvaluationResult
from .evaluator import BaseEvaluator, ScoringCriteria
from .leaderboard import Leaderboard, LeaderboardEntry

__all__ = [
    'ChallengeSystem',
    'Challenge',
    'ChallengeType',
    'ChallengeStatus',
    'Submission',
    'SubmissionStatus',
    'EvaluationResult',
    'BaseEvaluator',
    'ScoringCriteria',
    'Leaderboard',
    'LeaderboardEntry'
]
